
import os
import requests
import zipfile
from datetime import datetime

UPDATE_URL = "https://yourdomain.com/updates/sentinelit_update.zip"  # Replace with your update URL
DOWNLOAD_PATH = "updates/sentinelit_update.zip"
EXTRACT_PATH = "updates/"

def check_for_updates():
    print("[+] Checking for SentinelIT updates...")
    try:
        response = requests.get(UPDATE_URL, timeout=10)
        if response.status_code == 200:
            print("[+] Update available. Downloading...")
            with open(DOWNLOAD_PATH, "wb") as f:
                f.write(response.content)
            apply_update()
        else:
            print("[-] No update found or failed to connect.")
    except Exception as e:
        print(f"[!] Update check failed: {e}")

def apply_update():
    print("[*] Applying update...")
    try:
        with zipfile.ZipFile(DOWNLOAD_PATH, 'r') as zip_ref:
            zip_ref.extractall(EXTRACT_PATH)
        print("[+] Update applied successfully.")
        log_update()
    except Exception as e:
        print(f"[!] Failed to extract update: {e}")

def log_update():
    with open("update_log.txt", "a") as log:
        log.write(f"Update applied at {datetime.now()}
")

if __name__ == "__main__":
    check_for_updates()
