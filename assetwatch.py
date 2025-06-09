
import os
import time
import hashlib

ASSET_DIR = "SentinelIT_Build/assets"
LOG_FILE = "assetwatch_log.txt"
SCAN_INTERVAL = 60  # in seconds

def hash_file(filepath):
    try:
        with open(filepath, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception as e:
        return f"Error: {e}"

def scan_directory(directory):
    file_hashes = {}
    for root, _, files in os.walk(directory):
        for name in files:
            filepath = os.path.join(root, name)
            file_hashes[filepath] = hash_file(filepath)
    return file_hashes

def log_change(change_type, filepath):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{timestamp}] {change_type}: {filepath}\n")

def monitor_assets():
    previous_state = scan_directory(ASSET_DIR)
    print("[AssetWatch] Monitoring started...")

    while True:
        time.sleep(SCAN_INTERVAL)
        current_state = scan_directory(ASSET_DIR)

        added = set(current_state.keys()) - set(previous_state.keys())
        removed = set(previous_state.keys()) - set(current_state.keys())
        modified = {f for f in current_state if f in previous_state and current_state[f] != previous_state[f]}

        for f in added:
            log_change("Added", f)
        for f in removed:
            log_change("Removed", f)
        for f in modified:
            log_change("Modified", f)

        previous_state = current_state

if __name__ == "__main__":
    monitor_assets()
