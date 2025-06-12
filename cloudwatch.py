
# cloudwatch.py – Offline + Syncable Cloud Event Logger for SentinelIT

import json
import time
import os
from datetime import datetime

EVENT_LOG_PATH = "logs/cloud_events.json"
SYNC_LOG_PATH = "logs/cloud_sync_status.txt"
CLOUD_MIRROR = "cloud_mirror.json"  # Simulated mirror for cloud upload

# === Save Events Offline ===
def log_event(event_type, detail):
    os.makedirs("logs", exist_ok=True)
    entry = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "detail": detail
    }
    with open(EVENT_LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"[CLOUDWATCH] Event saved: {event_type} - {detail}")

# === Simulated Cloud Sync ===
def sync_to_cloud():
    if not os.path.exists(EVENT_LOG_PATH):
        print("[CLOUDWATCH] No events to sync.")
        return

    try:
        with open(EVENT_LOG_PATH, "r") as f:
            events = f.readlines()

        with open(CLOUD_MIRROR, "a") as cloudf:
            for line in events:
                cloudf.write(line)

        os.remove(EVENT_LOG_PATH)
        with open(SYNC_LOG_PATH, "a") as syncf:
            syncf.write(f"Synced {len(events)} events at {datetime.now().isoformat()}\n")
        print(f"[CLOUDWATCH] Synced {len(events)} events to cloud mirror.")
    except Exception as e:
        print(f"[CLOUDWATCH] Sync failed: {e}")

# === Scheduler ===
def start_cloudwatch(interval_seconds=300):
    def loop():
        while True:
            sync_to_cloud()
            time.sleep(interval_seconds)
    import threading
    threading.Thread(target=loop, daemon=True).start()
