
# packetshield.py – Real-time Packet Scanner with Basic DLP (Data Loss Prevention)

import socket
import threading
import re
from datetime import datetime

LOG_PATH = "logs/packetshield_log.txt"

# === DLP Keywords for Sensitive Info ===
dlp_patterns = [
    r"password",
    r"secret",
    r"confidential",
    r"credit\s*card",
    r"ssn|social\s*security",
    r"pin\s*code",
    r"api[_-]?key",
]

def log_packet(info):
    with open(LOG_PATH, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] {info}\n")
    print(f"[PACKETSHIELD] {info}")

# === Packet Analyzer ===
def analyze_packet(data):
    decoded = data.decode(errors='ignore')
    for pattern in dlp_patterns:
        if re.search(pattern, decoded, re.IGNORECASE):
            log_packet(f"DLP MATCH FOUND: '{pattern}' in packet -> {decoded[:100]}")
            return
    if "http" in decoded or "ftp" in decoded:
        log_packet(f"General packet: {decoded[:100]}")

# === Packet Sniffer ===
def packet_sniffer():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
        sock.bind(("0.0.0.0", 0))
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        sock.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
    except Exception as e:
        log_packet(f"Error starting sniffer: {e}")
        return

    while True:
        try:
            data, addr = sock.recvfrom(65535)
            analyze_packet(data)
        except Exception as e:
            log_packet(f"Sniffing error: {e}")

# === Thread Launcher ===
def start_packetshield():
    threading.Thread(target=packet_sniffer, daemon=True).start()
