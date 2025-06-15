
import json
import time
import os

THREAT_MEMORY_FILE = "threat_memory.json"
FINGERPRINT_FILE = "threat_fingerprint.json"
RESURG_LOG = "resurgent_threats.log"

def load_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return {}

def save_log(message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(RESURG_LOG, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

def detect_resurgent_patterns():
    memory = load_json(THREAT_MEMORY_FILE)
    fingerprints = load_json(FINGERPRINT_FILE)
    resurgent = []

    for cve_id, signature in memory.items():
        for pattern_id, pattern in fingerprints.items():
            if signature.get("dna") == pattern.get("dna") and signature.get("date") != pattern.get("date"):
                resurgent.append((cve_id, pattern_id))
                save_log(f"Resurgent exploit pattern detected: {cve_id} matches {pattern_id}")

    return resurgent

def main():
    print("[ResurgWatch] Monitoring for resurgent CVEs...")
    while True:
        detect_resurgent_patterns()
        time.sleep(3600)  # Check every hour

if __name__ == "__main__":
    main()
