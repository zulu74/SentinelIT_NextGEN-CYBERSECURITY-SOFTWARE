import os
import time
import getpass
import ctypes
from win10toast import ToastNotifier

# Setup notifier
toaster = ToastNotifier()

# USB quarantine folder
QUARANTINE_DIR = "C:/SentinelIT_Quarantine"
if not os.path.exists(QUARANTINE_DIR):
    os.makedirs(QUARANTINE_DIR)

# Simulated clearance password
CLEARANCE_PASSWORD = "63978zulu"

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def scan_usb():
    drives = [f"{d}:\" for d in "DEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:\")]
    return drives

def quarantine_drive(drive):
    os.system("taskkill /f /im explorer.exe")
    toaster.show_toast("USB Quarantine", f"Drive {drive} quarantined.", duration=5)
    suspicious_files = ["autorun.inf", "bootmgr.efi"]
    for root, _, files in os.walk(drive):
        for file in files:
            if file.lower() in suspicious_files:
                src = os.path.join(root, file)
                dst = os.path.join(QUARANTINE_DIR, file)
                try:
                    os.rename(src, dst)
                except:
                    pass

def unlock_drive():
    try:
        pwd = getpass.getpass("[USBWATCH] Enter clearance password to unlock USB: ")
        if pwd == CLEARANCE_PASSWORD:
            print("[USBWATCH] Access granted. Drive unlocked for use.")
            os.system("start explorer.exe")
        else:
            print("[USBWATCH] Access denied. Wrong password.")
    except Exception as e:
        print(f"[USBWATCH] Password prompt failed: {e}")

def monitor_usb():
    known = set(scan_usb())
    print("[USBWATCH] Monitoring for new USB devices...")
    while True:
        time.sleep(5)
        current = set(scan_usb())
        new_devices = current - known
        if new_devices:
            for drive in new_devices:
                print(f"[USBWATCH] USB device detected: {drive} -> Quarantining...")
                quarantine_drive(drive)
                unlock_drive()
        known = current

if __name__ == "__main__":
    if not is_admin():
        print("Administrator privileges required.")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", "python", __file__, None, 1)
    else:
        monitor_usb()