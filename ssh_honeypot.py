
# ssh_honeypot.py
import socket
import threading
from datetime import datetime
import os

LOG_FILE = "logs/ssh_honeypot_log.txt"
PORT = 2222  # Fake SSH port (non-standard)

os.makedirs("logs", exist_ok=True)

def log_attempt(ip, data):
    with open(LOG_FILE, "a") as log:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log.write(f"[{timestamp}] Attempt from {ip} - Data: {data}\n")

def handle_client(client_socket, addr):
    try:
        banner = "SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5\r\n"
        client_socket.send(banner.encode())
        data = client_socket.recv(1024).decode('utf-8', errors='ignore')
        log_attempt(addr[0], data)
    finally:
        client_socket.close()

def start_ssh_honeypot():
    print("[SSH Honeypot] Starting on port", PORT)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", PORT))
    server.listen(5)
    print("[SSH Honeypot] Listening for brute-force attempts...")

    while True:
        client, addr = server.accept()
        client_thread = threading.Thread(target=handle_client, args=(client, addr))
        client_thread.start()

# Uncomment below to run standalone
# if __name__ == "__main__":
#     start_ssh_honeypot()
