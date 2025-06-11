
# webdavwatch.py – SentinelIT Defense Module for WebDAV CVE-2025-33053
import subprocess
import logging
import os
import time
import platform

logging.basicConfig(filename="webdavwatch_log.txt", level=logging.INFO)

def disable_webclient_service():
    if platform.system() == "Windows":
        try:
            subprocess.call("sc stop WebClient", shell=True)
            subprocess.call("sc config WebClient start= disabled", shell=True)
            logging.info("[WebDAVWATCH] WebClient service disabled.")
        except Exception as e:
            logging.error(f"[WebDAVWATCH] Failed to disable WebClient: {e}")

def monitor_network_shares():
    logging.info("[WebDAVWATCH] Monitoring for suspicious UNC path activity...")
    while True:
        try:
            output = subprocess.check_output('net use', shell=True, text=True)
            for line in output.splitlines():
                if "\\" in line and "WebDAV" in line:
                    logging.warning(f"[WebDAVWATCH] Suspicious WebDAV connection: {line}")
        except Exception as e:
            logging.error(f"[WebDAVWATCH] Error reading network shares: {e}")
        time.sleep(30)

def main():
    print("[SentinelIT] WebDAV Exploit Defense Active.")
    disable_webclient_service()
    monitor_network_shares()

if __name__ == "__main__":
    main()
