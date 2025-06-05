
import os
import shutil
import time

def run():
    suspect_dir = "C:/opt/SentinelIT/suspects"
    quarantine_dir = "C:/opt/SentinelIT/quarantine"
    os.makedirs(suspect_dir, exist_ok=True)
    os.makedirs(quarantine_dir, exist_ok=True)

    for f in os.listdir(suspect_dir):
        full_path = os.path.join(suspect_dir, f)
        if os.path.isfile(full_path):
            shutil.move(full_path, os.path.join(quarantine_dir, f))
            print(f"[QUARANTINE] Moved {f} to secure zone.")
    print("[QUARANTINE] Sweep complete.")
