
import sys
import os
import pystray
from pystray import MenuItem as item
from PIL import Image
import subprocess
import threading

# Path to the tray icon image
ICON_PATH = "SentinelIT_logo.png"  # Place your PNG logo here

# Path to the SentinelIT executable or script to launch
APP_PATH = "phantomstaff.py"  # Update to your actual script

def run_app():
    subprocess.Popen(["python", APP_PATH], shell=True)

def on_quit(icon, item):
    icon.stop()

def setup_tray():
    image = Image.open(ICON_PATH)
    menu = (item('Launch SentinelIT', lambda icon, item: run_app()), item('Exit', on_quit))
    icon = pystray.Icon("SentinelIT", image, "SentinelIT", menu)
    icon.run()

def add_to_startup():
    import winreg
    startup_path = sys.argv[0]
    key = r"Software\Microsoft\Windows\CurrentVersion\Run"
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_SET_VALUE) as reg_key:
        winreg.SetValueEx(reg_key, "SentinelITTray", 0, winreg.REG_SZ, startup_path)

if __name__ == "__main__":
    threading.Thread(target=add_to_startup).start()
    setup_tray()
