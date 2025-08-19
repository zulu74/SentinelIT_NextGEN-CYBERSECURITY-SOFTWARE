#!/usr/bin/env python3
"""
usbwatch.py — USB Device Monitoring for SentinelIT

Features:
- Detects USB insertion/removal
- Scans for suspicious files and YARA matches
- Emits events to CloudWatch for logging and S3 sync
- Threaded background monitoring
"""

import threading
import time
from pathlib import Path

# Use your existing YARA scanning methods here
try:
    import yara
    YARA_AVAILABLE = True
except Exception:
    yara = None
    YARA_AVAILABLE = False

# Replace actual USB detection with psutil or pyudev if on Linux
import psutil

from cloudwatch import emit_event

SCAN_INTERVAL = 5  # seconds
MONITORED_PATHS = ["D:\\", "E:\\"]  # Example mount points for Windows

def scan_usb(mountpoint: str):
    """
    Simulated scan function for files in USB drive
    """
    suspicious_files = []
    yara_matches = []

    # Iterate files (simulate detection)
    for f in Path(mountpoint).rglob("*.*"):
        if "malware" in f.name.lower():
            suspicious_files.append(f)
            if YARA_AVAILABLE:
                yara_matches.append({"file": str(f), "hits": ["FakeRule1"]})

    return suspicious_files, yara_matches

def monitor_usb():
    emit_event("USBWatch", "module_start", {"module": "USBWatch"})
    print("[USBWatch] Monitoring USB devices...")

    known_devices = set()
    while True:
        for mount in MONITORED_PATHS:
            if Path(mount).exists():
                device_id = mount  # Simple simulation
                if device_id not in known_devices:
                    known_devices.add(device_id)
                    emit_event("USBWatch", "usb_insert", {"device": device_id, "mountpoint": mount})
                    suspicious_files, yara_matches = scan_usb(mount)

                    if suspicious_files or yara_matches:
                        emit_event("USBWatch", "usb_suspicious", {
                            "device": device_id,
                            "mountpoint": mount,
                            "heur_count": len(suspicious_files),
                            "yara_count": len(yara_matches)
                        })
                        for yh in yara_matches:
                            emit_event("USBWatch", "yara_usb_match", {
                                "device": device_id,
                                "file": yh.get("file"),
                                "hits": yh.get("hits")
                            })
                    else:
                        emit_event("USBWatch", "usb_clean", {"device": device_id, "mountpoint": mount})
        time.sleep(SCAN_INTERVAL)

def start():
    t = threading.Thread(target=monitor_usb, daemon=True)
    t.start()

def main():
    start()
    while True:
        time.sleep(60)

if __name__ == "__main__":
    main()


