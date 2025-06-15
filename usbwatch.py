
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
