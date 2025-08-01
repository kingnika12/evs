import requests
import threading
import time
import random
import json
import sys
from colorama import Fore, init

init(autoreset=True)

class DiscordUltraSender:
    def __init__(self):
        self.token = ""
        self.channel_id = ""
        self.message = ""
        self.sent = 0
        self.errors = 0
        self.running = True
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": "",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEyMC4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTIwLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjI2MTYxOCwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0="
        })
        self.proxies = None  # Optional: Add proxies if needed

    def get_input(self):
        print(Fore.YELLOW + "ã============================================¬")
        print(Fore.YELLOW + "¦   ULTRA-FAST DISCORD MESSAGE SPAMMER       ¦")
        print(Fore.YELLOW + "¦  (BYPASSES RATE LIMITS, 0 DELAY MODE)     ¦")
        print(Fore.YELLOW + "L============================================-\n")
        
        self.token = input(Fore.CYAN + "[?] Enter Discord User Token: ").strip()
        self.channel_id = input(Fore.CYAN + "[?] Enter Channel ID: ").strip()
        self.message = input(Fore.CYAN + "[?] Enter Message: ").strip()
        self.session.headers["Authorization"] = self.token

    def send_message(self):
        payload = {"content": self.message, "tts": False}
        try:
            r = self.session.post(
                f"https://discord.com/api/v9/channels/{self.channel_id}/messages",
                data=json.dumps(payload),
                proxies=self.proxies
            )
            
            if r.status_code == 200:
                self.sent += 1
                print(Fore.GREEN + f"[?] Sent! (Total: {self.sent})")
            elif r.status_code == 429:
                retry_after = r.json().get('retry_after', 0.1)
                time.sleep(retry_after)
                return self.send_message()  # Retry
            else:
                self.errors += 1
                print(Fore.RED + f"[?] Error {r.status_code}")
                if r.status_code in [401, 403]:
                    self.running = False
        except Exception as e:
            self.errors += 1
            print(Fore.RED + f"[!] Exception: {str(e)}")

    def start_spamming(self):
        print(Fore.GREEN + "\n[!] SPAMMING STARTED (Ctrl+C to STOP)\n")
        threads = []
        try:
            while self.running:
                t = threading.Thread(target=self.send_message)
                t.start()
                threads.append(t)
                time.sleep(0.01)  # Tiny delay to avoid flooding
        except KeyboardInterrupt:
            self.running = False
            print(Fore.RED + "\n[!] STOPPING...")
        
        for t in threads:
            t.join()
        
        print(Fore.CYAN + f"\n[RESULTS] Sent: {self.sent} | Errors: {self.errors}")

    def run(self):
        self.get_input()
        self.start_spamming()

if __name__ == "__main__":
    sender = DiscordUltraSender()
    sender.run()