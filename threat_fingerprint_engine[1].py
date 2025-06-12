
# threat_fingerprint_engine.py
import os
import hashlib
import datetime

FINGERPRINT_DB = "logs/threat_fingerprints.db"

def generate_fingerprint(payload, source="unknown"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fingerprint = hashlib.sha256(payload.encode()).hexdigest()
    entry = f"{timestamp} | {source} | {fingerprint} | {payload}\n"
    with open(FINGERPRINT_DB, "a") as f:
        f.write(entry)
    return fingerprint

def match_fingerprint(payload):
    current_fp = hashlib.sha256(payload.encode()).hexdigest()
    if not os.path.exists(FINGERPRINT_DB):
        return False
    with open(FINGERPRINT_DB, "r") as f:
        entries = f.readlines()
    for entry in entries:
        if current_fp in entry:
            return True
    return False

# Example test
if __name__ == "__main__":
    test_payload = "<script>alert(1)</script>"
    fp = generate_fingerprint(test_payload, source="honeypot_test")
    print("[+] Generated fingerprint:", fp)
    match = match_fingerprint(test_payload)
    print("[✓] Match found:", match)
