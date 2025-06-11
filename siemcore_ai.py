
# siemcore_ai.py - Advanced AI SIEM Engine for SentinelIT Phase 8
import os
import json
import time
import hashlib
import logging
from datetime import datetime

LOG_DIR = "logs"
MEMORY_FILE = "threat_memory.json"
SIEM_REPORT = "siem_summary_log.txt"
PATTERN_KEYS = ["usbwatch", "packetshield", "cmd_activity", "webdav", "ai_speed", "iamwatch", "cloudwatch", "trapengine"]

logging.basicConfig(filename=SIEM_REPORT, level=logging.INFO)

def load_logs():
    events = []
    for file in os.listdir(LOG_DIR):
        if file.endswith(".txt"):
            with open(os.path.join(LOG_DIR, file), "r", errors="ignore") as f:
                for line in f:
                    if any(k in line.lower() for k in PATTERN_KEYS):
                        events.append({
                            "source": file,
                            "line": line.strip(),
                            "hash": hashlib.md5(line.encode()).hexdigest(),
                            "timestamp": str(datetime.now())
                        })
    return events

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)

def generate_summary(events, memory):
    logging.info(f"\n==== SIEM Summary {datetime.now()} ====")
    seen_hashes = {m["hash"] for m in memory}
    new_threats = []

    for event in events:
        if event["hash"] not in seen_hashes:
            new_threats.append(event)
            logging.warning(f"[NEW] {event['source']} >> {event['line']}")
        else:
            logging.info(f"[MEM] {event['source']} >> {event['line']}")

    memory.extend(new_threats)
    return memory

def main():
    print("[SIEM AI] Starting pattern recognition SIEM engine...")
    while True:
        events = load_logs()
        memory = load_memory()
        memory = generate_summary(events, memory)
        save_memory(memory)
        time.sleep(120)

if __name__ == "__main__":
    main()
