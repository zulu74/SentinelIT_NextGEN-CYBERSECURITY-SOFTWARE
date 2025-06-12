
# rdp_honeypot.py
import socket
import threading
from datetime import datetime
import os

LOG_FILE = "logs/rdp_honeypot_log.txt"
PORT = 33890  # Fake RDP port (standard is 3389)

os.makedirs("logs", exist_ok=True)

def log_attempt(ip, data):
    with open(LOG_FILE, "a") as log:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log.write(f"[{timestamp}] Attempt from {ip} - Data: {data}\n")

def handle_client(client_socket, addr):
    try:
        # Simulate RDP protocol handshake start
        fake_banner = bytes.fromhex("0300000b06000100000000")
        client_socket.send(fake_banner)
        data = client_socket.recv(1024).hex()
        log_attempt(addr[0], data)
    finally:
        client_socket.close()

def start_rdp_honeypot():
    print("[RDP Honeypot] Starting on port", PORT)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", PORT))
    server.listen(5)
    print("[RDP Honeypot] Listening for RDP brute-force or scan attempts...")

    while True:
        client, addr = server.accept()
        client_thread = threading.Thread(target=handle_client, args=(client, addr))
        client_thread.start()

# Uncomment below to run standalone
# if __name__ == "__main__":
#     start_rdp_honeypot()
