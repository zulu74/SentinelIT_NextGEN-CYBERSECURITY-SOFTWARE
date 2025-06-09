
import logging
import shutil
import os

log_file = "C:/opt/SentinelIT/logs/backupvault.log"
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(message)s")

def run():
    print("[BACKUPVAULT] Auto-quarantine triggered for test threat.")
    quarantine_folder = "C:/opt/SentinelIT/quarantine"
    os.makedirs(quarantine_folder, exist_ok=True)
    dummy_file = os.path.join(quarantine_folder, "suspect_backup.txt")
    with open(dummy_file, "w") as f:
        f.write("Simulated infected data. Quarantined.")
    logging.warning("[BACKUPVAULT] Suspicious file backed up and quarantined.")
    print("[BACKUPVAULT] Threat isolated in secure vault.")
