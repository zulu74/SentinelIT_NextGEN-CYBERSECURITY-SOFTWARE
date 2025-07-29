# ransomdefender.py - Detects, contains, and mitigates ransomware and malware infections in SentinelIT

import os
import psutil
import shutil
import time
import hashlib
from datetime import datetime
from sentinelIT.Eventlogger import log_event  # Assumes you have this module

# Suspicious file extensions and ransom note keywords
SUSPICIOUS_EXTENSIONS = ['.locked', '.crypted', '.encrypted', '.enc', '.pay']
RANSOM_NOTE_KEYWORDS = ['ransom', 'decrypt', 'payment', 'bitcoin', 'recover']
QUARANTINE_DIR = os.path.join(os.getcwd(), 'quarantine')

if not os.path.exists(QUARANTINE_DIR):
    os.makedirs(QUARANTINE_DIR)

# Simulated hash database of known threats
KNOWN_VIRUS_SIGNATURES = {
    "e99a18c428cb38d5f260853678922e03",  # Example MD5 of known payload
    "6f1ed002ab5595859014ebf0951522d9"
}

def hash_file(filepath):
    try:
        with open(filepath, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return None

def detect_ransom_files(scan_path):
    threats = []
    for root, dirs, files in os.walk(scan_path):
        for file in files:
            full_path = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()
            if ext in SUSPICIOUS_EXTENSIONS or any(kw in file.lower() for kw in RANSOM_NOTE_KEYWORDS):
                threats.append(full_path)
            else:
                file_hash = hash_file(full_path)
                if file_hash and file_hash in KNOWN_VIRUS_SIGNATURES:
                    threats.append(full_path)
    return threats

def kill_suspicious_processes():
    killed = []
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            pname = proc.info['name'].lower()
            if any(word in pname for word in ["encrypt", "ransom", "locker"]):
                proc.kill()
                killed.append(pname)
                log_event("ransomdefender", f"Killed suspicious process: {pname}")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return killed

def quarantine_files(threat_paths):
    for path in threat_paths:
        try:
            filename = os.path.basename(path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_name = f"{timestamp}_{filename}"
            dest = os.path.join(QUARANTINE_DIR, new_name)
            shutil.move(path, dest)
            log_event("ransomdefender", f"Quarantined file: {path} -> {dest}")
        except Exception as e:
            log_event("ransomdefender", f"Failed to quarantine {path}: {e}")

def run_full_scan(scan_dir="C:/"):
    print("[RansomDefender] Starting full system scan...")
    log_event("ransomdefender", "Full scan started")

    # Detect suspicious files
    threats = detect_ransom_files(scan_dir)
    if threats:
        print(f"[RansomDefender] Detected threats: {len(threats)}")
        log_event("ransomdefender", f"Detected {len(threats)} threat files")

        # Quarantine
        quarantine_files(threats)
    else:
        print("[RansomDefender] No ransomware signatures found.")

    # Kill malicious processes
    killed = kill_suspicious_processes()
    print(f"[RansomDefender] Terminated {len(killed)} suspicious processes.")

    log_event("ransomdefender", "Scan completed")

def start():
    while True:
        run_full_scan("C:/")  # or use os.getcwd() or a config path
        time.sleep(1800)  # Every 30 minutes

if __name__ == "__main__":
    start()
