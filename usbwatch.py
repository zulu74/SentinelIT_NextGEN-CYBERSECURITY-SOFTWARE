
import os
import psutil
import time
import subprocess

scanned_drives = set()

def is_usb_drive(partition):
    return 'removable' in partition.opts.lower()

def scan_file(filepath):
    try:
        with open(filepath, 'rb') as f:
            content = f.read()
            if b'cmd' in content or b'powershell' in content or b'<script>' in content:
                return True
    except:
        pass
    return False

def alert_admin(message):
    print(f"[USBWatch] ALERT: {message}")

def open_explorer(drive_letter):
    try:
        subprocess.Popen(f'explorer {drive_letter}', shell=True)
        print(f"[USBWatch] USB {drive_letter} opened in File Explorer.")
    except Exception as e:
        print(f"[USBWatch] Could not open USB {drive_letter}: {e}")

print("[USBWatch] Monitoring for USB insertions...")

while True:
    current_drives = {p.device for p in psutil.disk_partitions() if is_usb_drive(p)}
    new_drives = current_drives - scanned_drives
    for drive in new_drives:
        print(f"[USBWatch] New USB detected: {drive}")
        infected = False
        for root, dirs, files in os.walk(drive):
            for file in files:
                filepath = os.path.join(root, file)
                if scan_file(filepath):
                    infected = True
                    alert_admin(f"Malicious file found: {filepath}")
                    break
            if infected:
                break
        if not infected:
            print(f"[USBWatch] USB {drive} is clean and ready.")
            open_explorer(drive)
        scanned_drives.add(drive)
    time.sleep(10)
