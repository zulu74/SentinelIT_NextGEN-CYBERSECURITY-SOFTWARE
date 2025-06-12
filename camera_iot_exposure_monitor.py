
# camera_iot_exposure_monitor.py
import socket
import requests
from datetime import datetime
import os

LOG_FILE = "logs/iot_exposure_log.txt"
COMMON_PORTS = [554, 80, 81, 88, 8080, 443]
IOT_KEYWORDS = ["camera", "hikvision", "ipcam", "dvr", "onvif", "rtsp", "video", "stream"]

os.makedirs("logs", exist_ok=True)

def log_exposure(ip, port, service):
    with open(LOG_FILE, "a") as log:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log.write(f"[{timestamp}] IP: {ip}, Port: {port}, Service: {service}\n")

def scan_host(ip):
    for port in COMMON_PORTS:
        try:
            sock = socket.create_connection((ip, port), timeout=2)
            sock.close()

            # Try grabbing headers
            try:
                url = f"http://{ip}:{port}"
                r = requests.get(url, timeout=2)
                banner = r.text[:100].lower()

                if any(keyword in banner for keyword in IOT_KEYWORDS):
                    log_exposure(ip, port, banner)
            except:
                pass

        except:
            continue

def monitor_local_subnet(subnet="192.168.0."):
    print("[Camera/IoT Monitor] Scanning local subnet for exposed devices...")
    for i in range(1, 255):
        ip = f"{subnet}{i}"
        scan_host(ip)

# Uncomment to run standalone
# if __name__ == "__main__":
#     monitor_local_subnet()
