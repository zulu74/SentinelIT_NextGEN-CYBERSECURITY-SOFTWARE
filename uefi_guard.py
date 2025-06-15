
import subprocess
import hashlib
import time
import os
from datetime import datetime

# Path to store the UEFI firmware hash for baseline
BASELINE_HASH_PATH = "logs/uefi_baseline.hash"
ALERT_LOG_PATH = "logs/uefi_alerts.log"

def get_firmware_hash():
    try:
        result = subprocess.run(["powershell", "-Command", "Get-WmiObject -Class Win32_BIOS | Select-Object -ExpandProperty SMBIOSBIOSVersion"],
                                capture_output=True, text=True)
        firmware_data = result.stdout.strip()
        return hashlib.sha256(firmware_data.encode()).hexdigest()
    except Exception as e:
        return None

def load_baseline_hash():
    if os.path.exists(BASELINE_HASH_PATH):
        with open(BASELINE_HASH_PATH, "r") as f:
            return f.read().strip()
    return None

def save_baseline_hash(hash_value):
    os.makedirs(os.path.dirname(BASELINE_HASH_PATH), exist_ok=True)
    with open(BASELINE_HASH_PATH, "w") as f:
        f.write(hash_value)

def log_alert(message):
    os.makedirs(os.path.dirname(ALERT_LOG_PATH), exist_ok=True)
    with open(ALERT_LOG_PATH, "a") as f:
        f.write(f"{datetime.now()} - ALERT: {message}\n")

def monitor_uefi():
    current_hash = get_firmware_hash()
    if current_hash is None:
        log_alert("Could not retrieve UEFI firmware data.")
        return

    baseline_hash = load_baseline_hash()
    if baseline_hash is None:
        save_baseline_hash(current_hash)
        print("[UEFI GUARD] Baseline hash saved.")
    elif current_hash != baseline_hash:
        log_alert("UEFI/BIOS Firmware mismatch detected! Possible tampering.")
        print("[UEFI GUARD] ALERT: Firmware has changed!")
    else:
        print("[UEFI GUARD] Firmware verified. No changes detected.")

if __name__ == "__main__":
    monitor_uefi()
