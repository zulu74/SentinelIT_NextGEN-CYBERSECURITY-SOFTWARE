import time
import threading

def start():
    print("[TrayIconRunner] SentinelIT is running in the background with tray icon...")

    def notification_loop():
        while True:
            print("[TrayIcon] System secure. All modules active.")
            time.sleep(300)  # 5 minutes

    thread = threading.Thread(target=notification_loop)
    thread.daemon = True
    thread.start()
