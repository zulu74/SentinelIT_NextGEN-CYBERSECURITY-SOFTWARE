# ftpwatch.py – Monitors FTP access and enforces secondary authentication

import socket
import threading
import time
from authgate import AuthGate
from sentinelIT.Eventlogger import log_event

AUTHORIZED_IPS = ["127.0.0.1"]  # Add trusted IPs here
FTP_PORT = 21
SCAN_INTERVAL = 10  # seconds

class FTPWatcher:
    def __init__(self):
        self.gate = AuthGate()

    def scan_ports(self):
        while True:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex(("localhost", FTP_PORT))
                    if result == 0:
                        log_event("ftpwatch", f"FTP service detected on port {FTP_PORT}")
                        self.auth_check()
                    else:
                        print("[FTPWatch] FTP not active")
            except Exception as e:
                log_event("ftpwatch", f"Error scanning FTP: {e}")
            time.sleep(SCAN_INTERVAL)

    def auth_check(self):
        print("\n[FTPWatch] FTP access detected. Verifying secondary auth...")
        if self.gate.authenticate("ftp"):
            print("[FTPWatch] Access allowed")
        else:
            log_event("ftpwatch", "Unauthorized FTP access blocked")
            print("[FTPWatch] Access denied. Session terminated.")
            self.block_ftp()

    def block_ftp(self):
        # Optional: Stop FTP service or kill process
        log_event("ftpwatch", "(Simulated) FTP service shutdown")
        print("[FTPWatch] FTP service would be shut down here (placeholder).")

# ✅ This allows `ultimate_main.py` to launch it
def start():
    watcher = FTPWatcher()
    thread = threading.Thread(target=watcher.scan_ports)
    thread.daemon = True
    thread.start()
    while True:
        time.sleep(60)

# ✅ For standalone testing
if __name__ == "__main__":
    start()

