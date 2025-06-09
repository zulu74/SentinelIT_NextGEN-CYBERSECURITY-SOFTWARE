
# forensicswatch.py - SentinelIT Forensic Logging Module

import os
import hashlib
import json
from datetime import datetime

FORENSIC_LOG = "logs/forensics_log.json"

def calculate_file_hash(filepath):
    try:
        with open(filepath, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception as e:
        return f"ERROR: {e}"

def log_forensic_event(file_path, event_type="scan"):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "file": file_path,
        "hash": calculate_file_hash(file_path) if os.path.isfile(file_path) else "N/A"
    }
    os.makedirs(os.path.dirname(FORENSIC_LOG), exist_ok=True)
    try:
        if not os.path.exists(FORENSIC_LOG):
            with open(FORENSIC_LOG, "w") as f:
                json.dump([entry], f, indent=4)
        else:
            with open(FORENSIC_LOG, "r+") as f:
                data = json.load(f)
                data.append(entry)
                f.seek(0)
                json.dump(data, f, indent=4)
    except Exception as e:
        print(f"[Forensics] Error writing log: {e}")

def run_forensics():
    print("[FORENSICSWATCH] Running basic forensic scan on current directory...")
    for file in os.listdir():
        if file.endswith(".py") or file.endswith(".exe"):
            log_forensic_event(file)
    print("[FORENSICSWATCH] Forensic scan completed. Logs written.")
