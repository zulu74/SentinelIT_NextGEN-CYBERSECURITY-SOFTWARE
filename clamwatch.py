
import os
import subprocess
import time
from datetime import datetime

SCAN_DIR = "C:\\Users\\zxola\\Downloads"  # You can change this
LOG_FILE = "clamav_log.txt"
CLAMSCAN_PATH = "C:\\ClamAV\\clamscan.exe"

def log_event(message):
    with open(LOG_FILE, "a") as log:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log.write(f"[{timestamp}] {message}\n")

def scan_with_clamav():
    try:
        print("🛡️ Starting ClamAV scan...")
        result = subprocess.run(
            [CLAMSCAN_PATH, "-r", SCAN_DIR],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        log_event(result.stdout)
        print("✅ Scan complete. Log updated.")
    except Exception as e:
        log_event(f"ERROR: {e}")
        print(f"❌ Error during scan: {e}")

if __name__ == "__main__":
    while True:
        scan_with_clamav()
        time.sleep(3600)  # Scan every hour
