
# edrwatch.py - SentinelIT Endpoint Detection and Response Module

import os
import time
import json
import hashlib
from datetime import datetime

LOG_FILE = "logs/edr_activity_log.json"

def calculate_hash(data):
    return hashlib.sha256(data.encode()).hexdigest()

def log_edr_activity(activity_type, details):
    timestamp = datetime.utcnow().isoformat()
    entry = {
        "timestamp": timestamp,
        "activity_type": activity_type,
        "details": details,
        "hash": calculate_hash(f"{timestamp}{activity_type}{details}")
    }
    with open(LOG_FILE, "a") as f:
        json.dump(entry, f)
        f.write("\n")

def monitor_processes():
    processes = os.popen('tasklist').readlines()
    for process in processes[3:]:
        if "powershell" in process.lower() or "cmd.exe" in process.lower():
            log_edr_activity("suspicious_process", process.strip())

def run_edr_monitor():
    print("[EDR-WATCH] Monitoring for suspicious endpoint activity...")
    for _ in range(3):  # Simulate 3 scans for demo
        monitor_processes()
        time.sleep(5)

if __name__ == "__main__":
    run_edr_monitor()
