
import os
import psutil
import time
import getpass
import re
from datetime import datetime

# Suspicious code patterns
suspicious_patterns = [
    r'<script>.*?</script>',           # XSS scripts
    r'powershell.*-enc',               # Encoded PowerShell
    r'(Invoke-WebRequest|IEX)',        # PowerShell downloaders
    r'cmd\.exe',                      # Direct CMD calls
    r'(net user|net localgroup)',      # User/group enumeration
    r'(Base64|base64)',                # Base64 content often used in payloads
]

# Config
PASSWORD = "63978zulu"
LOG_FILE = "usb_log.txt"
SCAN_FOLDER = "E:/"

def log_event(event):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now()} - {event}\n")

def scan_usb(path):
    for root, dirs, files in os.walk(path):
        for file in files:
            try:
                full_path = os.path.join(root, file)
                with open(full_path, 'r', errors='ignore') as f:
                    content = f.read()
                    for pattern in suspicious_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            log_event(f"Suspicious pattern '{pattern}' detected in file: {full_path}")
                            print(f"Suspicious file detected: {file}")
            except Exception as e:
                continue

def request_password():
    for attempt in range(3):
        user_input = getpass.getpass("Enter password to unlock USB: ")
        if user_input == PASSWORD:
            print("Access granted.")
            return True
        else:
            print("Incorrect password.")
    print("Too many failed attempts. USB access denied.")
    return False

def monitor_usb():
    print("Monitoring USB ports... Press Ctrl+C to stop.")
    known_devices = set([disk.device for disk in psutil.disk_partitions()])
    while True:
        current_devices = set([disk.device for disk in psutil.disk_partitions()])
        new_devices = current_devices - known_devices
        if new_devices:
            for dev in new_devices:
                user = getpass.getuser()
                log_event(f"USB inserted at {dev} by user {user}")
                print(f"USB detected: {dev}. Quarantining and scanning...")
                scan_usb(dev)
                if request_password():
                    print(f"{dev} unlocked for use.")
                else:
                    print(f"{dev} remains locked.")
        known_devices = current_devices
        time.sleep(5)

if __name__ == "__main__":
    monitor_usb()
