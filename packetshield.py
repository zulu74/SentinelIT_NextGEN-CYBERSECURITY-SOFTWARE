
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
=======
# packetshield.py - Passive Packet Monitoring for SentinelIT (Phase 8)
import scapy.all as scapy
import logging
from datetime import datetime

log_file = "packetshield_log.txt"
logging.basicConfig(filename=log_file, level=logging.INFO)

MALICIOUS_SIGNATURES = [
    "nmap", "nikto", "sqlmap", "malware", "powershell", "curl", "wget", "payload", "exploit"
]

def detect_payload(packet):
    try:
        if packet.haslayer(scapy.Raw):
            payload = packet[scapy.Raw].load.decode(errors='ignore').lower()
            for signature in MALICIOUS_SIGNATURES:
                if signature in payload:
                    logging.warning(f"[{datetime.now()}] Suspicious traffic detected: {signature.upper()} in payload")
                    print(f"[!] Alert: Suspicious traffic: {signature.upper()} detected")
                    break
    except Exception as e:
        pass  # ignore decode errors

def main():
    print("[PacketShield] Passive packet monitoring started...")
    scapy.sniff(filter="ip", prn=detect_payload, store=0)

if __name__ == "__main__":
    main()

