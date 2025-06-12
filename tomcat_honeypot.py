
# tomcat_honeypot.py
import socket
import threading
from datetime import datetime
import os

LOG_FILE = "logs/tomcat_honeypot_log.txt"
PORT = 8081  # Honeypot Tomcat port

os.makedirs("logs", exist_ok=True)

def log_attempt(ip, data):
    with open(LOG_FILE, "a") as log:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log.write(f"[{timestamp}] Attempt from {ip} - Data: {data}\n")

def handle_client(client_socket, addr):
    try:
        data = client_socket.recv(1024).decode('utf-8', errors='ignore')
        log_attempt(addr[0], data)
        response = "HTTP/1.1 401 Unauthorized\r\nWWW-Authenticate: Basic realm=\"Tomcat\"\r\n\r\nUnauthorized"
        client_socket.send(response.encode())
    finally:
        client_socket.close()

def start_tomcat_honeypot():
    print("[Tomcat Honeypot] Starting on port", PORT)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", PORT))
    server.listen(5)
    print("[Tomcat Honeypot] Listening for brute-force attempts...")

    while True:
        client, addr = server.accept()
        client_thread = threading.Thread(target=handle_client, args=(client, addr))
        client_thread.start()

# Uncomment below to run standalone
# if __name__ == "__main__":
#     start_tomcat_honeypot()
