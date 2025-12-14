#!/usr/bin/env python3
"""
AUTHORIZED HTTP LOAD / STRESS TEST SCRIPT (GET ONLY)

⚠️ WARNING:
This script is STRICTLY for testing websites that YOU OWN or have
EXPLICIT WRITTEN PERMISSION to test. Unauthorized use against systems
you do not control may be illegal.

Features:
- Permission confirmation required
- Async HTTP GET requests (aiohttp + asyncio)
- User-Agent rotation
- Safe defaults & connection limits
- Graceful Ctrl+C handling
- Live progress (RPS)
- Summary report on exit

Python 3.9+
Cross-platform (Windows / Linux / macOS)
"""

import asyncio
import aiohttp
import random
import time
import sys
from urllib.parse import urlparse

# -------------------------
# USER AGENTS (ROTATED)
# -------------------------
USER_AGENTS = [
    # Desktop
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",

    # Mobile
    "Mozilla/5.0 (Linux; Android 13; SM-A032F) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/118.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
]

# -------------------------
# SAFETY DEFAULTS
# -------------------------
DEFAULT_CONCURRENCY = 10        # Safe default
REQUEST_TIMEOUT = 10            # seconds
MAX_CONNECTIONS = 50            # aiohttp connector limit
PROGRESS_INTERVAL = 1.0         # seconds

# -------------------------
# GLOBAL STATS
# -------------------------
total_requests = 0
success_responses = 0
failed_responses = 0
status_codes = {}
start_time = None
stop_event = asyncio.Event()


# -------------------------
# UTILS
# -------------------------
def validate_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


def print_exit(msg: str):
    print(msg)
    sys.exit(0)


# -------------------------
# WORKER TASK
# -------------------------
async def worker(session: aiohttp.ClientSession, url: str):
    global total_requests, success_responses, failed_responses, status_codes

    while not stop_event.is_set():
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "*/*",
            "Connection": "keep-alive",
        }

        try:
            async with session.get(url, headers=headers) as resp:
                total_requests += 1
                status_codes[resp.status] = status_codes.get(resp.status, 0) + 1

                if 200 <= resp.status < 400:
                    success_responses += 1
                else:
                    failed_responses += 1

                # Read response to completion (important for fairness)
                await resp.read()

        except asyncio.CancelledError:
            return
        except Exception:
            total_requests += 1
            failed_responses += 1


# -------------------------
# PROGRESS REPORTER
# -------------------------
async def progress_reporter():
    last_count = 0
    last_time = time.time()

    while not stop_event.is_set():
        await asyncio.sleep(PROGRESS_INTERVAL)

        now = time.time()
        diff = total_requests - last_count
        elapsed = now - last_time
        rps = diff / elapsed if elapsed > 0 else 0.0

        last_count = total_requests
        last_time = now

        print(
            f"[LIVE] Total: {total_requests} | "
            f"OK: {success_responses} | "
            f"Fail: {failed_responses} | "
            f"RPS: {rps:.2f}",
            flush=True
        )


# -------------------------
# MAIN ASYNC LOGIC
# -------------------------
async def run_test(url: str, duration: int, concurrency: int):
    global start_time
    start_time = time.time()

    connector = aiohttp.TCPConnector(
        limit=MAX_CONNECTIONS,
        ssl=False
    )

    timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)

    async with aiohttp.ClientSession(
        connector=connector,
        timeout=timeout
    ) as session:

        workers = [
            asyncio.create_task(worker(session, url))
            for _ in range(concurrency)
        ]

        reporter = asyncio.create_task(progress_reporter())

        try:
            if duration > 0:
                await asyncio.sleep(duration)
                stop_event.set()
            else:
                # Run until Ctrl+C
                await stop_event.wait()

        except KeyboardInterrupt:
            stop_event.set()

        finally:
            for w in workers:
                w.cancel()
            reporter.cancel()

            await asyncio.gather(*workers, return_exceptions=True)
            await asyncio.gather(reporter, return_exceptions=True)


# -------------------------
# ENTRY POINT
# -------------------------
def main():
    print("=== AUTHORIZED WEBSITE LOAD TEST TOOL ===\n")

    url = input("Enter the website URL you want to test: ").strip()
    if not validate_url(url):
        print_exit("Invalid URL format. Use http:// or https://")

    print("\nWARNING:")
    print("You must OWN this website or have EXPLICIT PERMISSION to test it.")
    confirm = input('Type "YES" to confirm permission: ').strip()

    if confirm != "YES":
        print_exit("Permission not confirmed. Exiting.")

    try:
        duration = int(
            input(
                "\nEnter test duration in seconds "
                "(enter 0 to run until manually stopped): "
            ).strip()
        )
        if duration < 0:
            raise ValueError
    except ValueError:
        print_exit("Invalid duration value.")

    concurrency_input = input(
        f"\nEnter number of concurrent requests "
        f"(default {DEFAULT_CONCURRENCY}): "
    ).strip()

    if concurrency_input == "":
        concurrency = DEFAULT_CONCURRENCY
    else:
        try:
            concurrency = int(concurrency_input)
            if concurrency <= 0:
                raise ValueError
        except ValueError:
            print_exit("Invalid concurrency value.")

    print("\nStarting authorized load test...")
    print("Press Ctrl+C to stop manually.\n")

    try:
        asyncio.run(run_test(url, duration, concurrency))
    except KeyboardInterrupt:
        pass

    total_time = time.time() - start_time if start_time else 0

    print("\n=== TEST SUMMARY ===")
    print(f"Target URL: {url}")
    print(f"Duration: {total_time:.2f} seconds")
    print(f"Total requests sent: {total_requests}")
    print(f"Successful responses: {success_responses}")
    print(f"Failed responses: {failed_responses}")
    print("HTTP status codes:")
    for code, count in sorted(status_codes.items()):
        print(f"  {code}: {count}")

    print("\nTest finished safely.")


if __name__ == "__main__":
    main()
