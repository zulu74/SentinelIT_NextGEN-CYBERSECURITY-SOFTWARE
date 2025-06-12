
# defensepack.py – Combines quarantine, autorespond, rollback features

import os
import json
import time
from datetime import datetime

# === Quarantine Mechanism ===
def quarantine_file(file_path):
    quarantine_dir = "quarantine"
    os.makedirs(quarantine_dir, exist_ok=True)
    base_name = os.path.basename(file_path)
    new_path = os.path.join(quarantine_dir, base_name)
    try:
        os.rename(file_path, new_path)
        log_action("Quarantined", file_path)
        return True
    except Exception as e:
        log_action("Quarantine Failed", str(e))
        return False

# === Auto Response System ===
def auto_respond(event):
    if event.get("decision") == "ALERT":
        reason = event.get("reason", "Unspecified")
        user = event["event"].get("user", "unknown")
        log_action("AutoRespond Alert", f"User={user}, Reason={reason}")
        # Trigger rollback or shutdown actions here
        return True
    return False

# === Rollback Dummy Feature ===
def rollback_system_state():
    log_action("Rollback", "System state rollback initialized (simulated).")
    time.sleep(2)
    return True

# === Log Helper ===
def log_action(action, detail):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "detail": detail
    }
    os.makedirs("logs", exist_ok=True)
    with open("logs/defensepack_log.json", "a") as logf:
        logf.write(json.dumps(log_entry) + "\n")
    print(f"[DEFENSEPACK] {action}: {detail}")
