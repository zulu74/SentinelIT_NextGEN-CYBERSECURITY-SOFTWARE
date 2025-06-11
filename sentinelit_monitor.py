
import sys
import os
import pystray
from pystray import MenuItem as item
from PIL import Image
import subprocess
import threading
import winreg
import logging
import time

ICON_PATH = "SentinelIT_logo.png"
MODULE_PATH = "ultimate_main.py"

def restore_cmd_access():
    try:
        reg_path = r"Software\\Policies\\Microsoft\\Windows\\System"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
            winreg.SetValueEx(key, "DisableCMD", 0, winreg.REG_DWORD, 0)
        print("[SentinelIT] CMD access restored.")
    except Exception as e:
        print(f"[SentinelIT] Failed to restore CMD: {e}")

def monitor_cmd_activity():
    logging.basicConfig(filename="cmd_activity_log.txt", level=logging.INFO)
    while True:
        # Placeholder for future detection (example simulated log)
        logging.info("Monitoring CMD usage...")
        time.sleep(10)

def launch_sentinelit():
    try:
        subprocess.Popen(["python", MODULE_PATH], shell=True)
    except Exception as e:
        print(f"Failed to launch SentinelIT: {e}")

def exit_tray(icon, item):
    icon.stop()

def create_tray():
    image = Image.open(ICON_PATH)
    menu = (
        item("Launch SentinelIT", lambda icon, item: launch_sentinelit()),
        item("Exit", exit_tray)
    )
    icon = pystray.Icon("SentinelIT", image, "SentinelIT Monitor", menu)
    icon.run()

def add_to_startup():
    try:
        import winreg
        startup_path = os.path.abspath(sys.argv[0])
        key = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_SET_VALUE) as reg_key:
            winreg.SetValueEx(reg_key, "SentinelITMonitor", 0, winreg.REG_SZ, startup_path)
    except Exception as e:
        print(f"Startup registration failed: {e}")

if __name__ == "__main__":
    threading.Thread(target=restore_cmd_access).start()
    threading.Thread(target=monitor_cmd_activity, daemon=True).start()
    threading.Thread(target=add_to_startup).start()
    create_tray()
