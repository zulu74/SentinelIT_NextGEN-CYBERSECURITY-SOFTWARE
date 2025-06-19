import time
import random

def start():
    print("[Quarantine] Monitoring system for files and threats requiring isolation...")

    actions = [
        "Suspicious file quarantined: payload.exe",
        "Malicious script isolated: worm.js",
        "Encrypted ransomware file moved to quarantine zone",
        "Unauthorized USB file transferred to secure quarantine",
        "Registry anomaly detected and isolated"
    ]

    while True:
        print(f"[Quarantine Notice] {random.choice(actions)}")
        time.sleep(6)
