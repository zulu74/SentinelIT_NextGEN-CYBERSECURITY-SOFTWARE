
# liveboard.py – Real-Time AI Dashboard for SentinelIT

import os
import json
import time
from datetime import datetime

LOG_DIR = "logs"
AI_LOG = os.path.join(LOG_DIR, "ai_threat_log.json")
DLP_LOG = os.path.join(LOG_DIR, "packetshield_log.txt")
CLOUD_SYNC_LOG = os.path.join(LOG_DIR, "cloud_sync_status.txt")

def read_json_lines(filepath, limit=10):
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r") as f:
        lines = f.readlines()[-limit:]
        return [json.loads(line) for line in lines if line.strip()]

def read_text_lines(filepath, limit=10):
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r") as f:
        return f.readlines()[-limit:]

def display_dashboard():
    print("\n=== SENTINELIT LIVEBOARD ===")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print("\n[AI THREATS]")
    for event in read_json_lines(AI_LOG):
        print(f"- {event['timestamp'][:19]} | {event['action']}: {event['detail']}")

    print("\n[DLP PACKETS]")
    for line in read_text_lines(DLP_LOG):
        print(f"- {line.strip()}")

    print("\n[CLOUD SYNC]")
    for line in read_text_lines(CLOUD_SYNC_LOG):
        print(f"- {line.strip()}")

    print("="*33)

def run_dashboard(interval=10):
    try:
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            display_dashboard()
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n[LiveBoard] Shutting down.")
