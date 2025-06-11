
# ultimate_main.py - SentinelIT Master Launcher

import threading
import time
import subprocess
from lockdown import lockdown_protocol

def main():
    # Show splash screen
    try:
        subprocess.Popen(["python", "splash_screen.py"], shell=True)
        time.sleep(3.5)  # Let splash finish before other modules load
    except Exception as e:
        print(f"[!] Splash screen failed: {e}")

    print("[SentinelIT] Starting SentinelIT Ultimate...")

    # Lockdown protocol
    try:
        lockdown_protocol()
    except Exception as e:
        print(f"[!] Lockdown error: {e}")

    # Start monitor tray icon (non-blocking)
    try:
        threading.Thread(
            target=lambda: subprocess.Popen(["python", "sentinelit_monitor.py"], shell=True),
            daemon=True
        ).start()
    except Exception as e:
        print(f"[!] Monitor launch failed: {e}")

    # Launch BeEF (optional if on Kali)
    try:
        threading.Thread(
            target=lambda: subprocess.Popen(["python", "BeEF.py"], shell=True),
            daemon=True
        ).start()
    except Exception as e:
        print(f"[!] BeEF not available: {e}")

    # Launch cloudwatch (optional)
    try:
        threading.Thread(
            target=lambda: subprocess.Popen(["python", "cloudwatch.py"], shell=True),
            daemon=True
        ).start()
    except Exception as e:
        print(f"[!] CloudWatch not available: {e}")

    # AI booster + system monitor
    try:
        threading.Thread(
            target=lambda: subprocess.Popen(["python", "ai_speed_monitor.py"], shell=True),
            daemon=True
        ).start()
    except Exception as e:
        print(f"[!] AI monitor not active: {e}")

    # WebDAV exploit defense
    try:
        threading.Thread(
            target=lambda: subprocess.Popen(["python", "webdavwatch.py"], shell=True),
            daemon=True
        ).start()
    except Exception as e:
        print(f"[!] WebDAV defense not active: {e}")

    print("[SentinelIT] All modules launched. System secure.")
    while True:
        time.sleep(10)

if __name__ == "__main__":
    main()
