
# ipwatch.py - Detect scanning from known cloud hosts (AWS, GCP, Azure)
import requests
import time
import logging
import socket

logging.basicConfig(filename="ipwatch_log.txt", level=logging.INFO)

# Simulated known cloud IPs (usually loaded from threat intel feeds or GREYNOISE)
CLOUD_IP_PATTERNS = [
    "52.", "3.", "13.", "18.", "34.",  # AWS
    "35.", "104.", "107.",             # GCP
    "20.", "40.", "51.", "168."        # Azure
]

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "0.0.0.0"

def scan_incoming_ips():
    print("[IPWATCH] Monitoring for inbound cloud-hosted scanning patterns...")
    while True:
        try:
            connections = socket.getaddrinfo(socket.gethostname(), None)
            for conn in connections:
                ip = conn[4][0]
                if any(ip.startswith(prefix) for prefix in CLOUD_IP_PATTERNS):
                    logging.warning(f"[IPWATCH] Cloud scan detected from: {ip}")
        except Exception as e:
            logging.error(f"[IPWATCH] Error: {e}")
        time.sleep(30)

def main():
    print("[SentinelIT] IPWATCH activated.")
    local_ip = get_local_ip()
    logging.info(f"[IPWATCH] Local IP: {local_ip}")
    scan_incoming_ips()

if __name__ == "__main__":
    main()
