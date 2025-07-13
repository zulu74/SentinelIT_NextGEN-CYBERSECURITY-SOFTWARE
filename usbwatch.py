
import os
import time
import psutil

scanned_drives = set()

def scan_file(filepath):
    # Simulated scan logic (replace with real AV or heuristic scan)
    with open(filepath, 'rb') as f:
        content = f.read()
        if b"malicious" in content or filepath.lower().endswith("setup.exe"):
            return True
    return False

def alert_admin(message):
    print(f"[USBWatch][ALERT] {message}")

def monitor_usb():
    print("[USBWatch] Monitoring for USB insertions...")
    while True:
        try:
            current_drives = {d.device for d in psutil.disk_partitions() if 'removable' in d.opts}
            new_drives = current_drives - scanned_drives

            for drive in new_drives:
                scanned_drives.add(drive)
                print(f"[USBWatch] New USB detected: {drive}")
                infected = False
                for root, dirs, files in os.walk(drive):
                    for file in files:
                        filepath = os.path.join(root, file)
                        try:
                            if scan_file(filepath):
                                alert_admin(f"Malicious file found: {filepath}")
                                infected = True
                        except Exception as e:
                            print(f"[USBWatch] Error scanning {filepath}: {e}")
                if not infected:
                    print(f"[USBWatch] USB {drive} is clean and ready to use.")

            time.sleep(10)
        except KeyboardInterrupt:
            print("[USBWatch] Monitoring interrupted by user.")
            break

if __name__ == "__main__":
    monitor_usb()

import time
from datetime import datetime
import random

# Simulated USB insertions
usb_events = [
    {"device": "Kingston USB", "serial": "SN-4459X", "user": "Admin", "risk": "Low"},
    {"device": "Sandisk Cruzer", "serial": "SN-9021Z", "user": "Analyst1", "risk": "Medium"},
    {"device": "Unrecognized Device", "serial": "SN-???", "user": "Unknown", "risk": "High"},
    {"device": "Lexar USB", "serial": "SN-7842L", "user": "Staff04", "risk": "Low"},
]

def start():
    print("[USBWATCH] Monitoring USB ports for activity...\n")
    for _ in range(5):
        event = random.choice(usb_events)
        print(f"[USBWATCH] Device Detected: {event['device']} | Serial: {event['serial']} | User: {event['user']} | Risk Level: {event['risk']} | Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        if event["risk"] == "High":
            print("[ALERT] High-risk USB device inserted. Initiating lockdown sequence and alert dispatch...\n")
        time.sleep(4)

if __name__ == "__main__":
    start()

