
# militaryshield.py – Military-Grade Cyber Defense Extension for SentinelIT

from pathlib import Path
import hashlib
import os
import time
import json
from datetime import datetime
from patternengine import run_patternengine

LOG_FILE = "sentinel_military_logs.json"
HASH_CHAIN_FILE = "log_hash_chain.txt"

def calculate_hash(content):
    return hashlib.sha256(content.encode()).hexdigest()

def append_log_with_hash(entry):
    log = {
        "timestamp": datetime.utcnow().isoformat(),
        "entry": entry
    }

    hash_chain = []

    if Path(HASH_CHAIN_FILE).exists():
        with open(HASH_CHAIN_FILE, "r") as f:
            hash_chain = f.read().splitlines()

    entry_json = json.dumps(log)
    current_hash = calculate_hash(entry_json)

    if hash_chain:
        current_hash = calculate_hash(hash_chain[-1] + current_hash)

    hash_chain.append(current_hash)

    with open(HASH_CHAIN_FILE, "w") as f:
        f.write("\n".join(hash_chain))

    with open(LOG_FILE, "a") as f:
        f.write(entry_json + "\n")

def analyze_behavior():
    return [
        "Brute force login attempt",
        "Unusual admin login time",
        "Process injection detected"
    ]

def simulate_threat_hunting():
    suspicious_behaviors = analyze_behavior()
    for behavior in suspicious_behaviors:
        append_log_with_hash({
            "type": "threat_detected",
            "detail": behavior
        })

if __name__ == "__main__":
    append_log_with_hash({"msg": "🚨 MilitaryShield module started."})
    run_patternengine()
    simulate_threat_hunting()
