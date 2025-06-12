
# ai_core.py – Unified AI Threat Engine for SentinelIT
# Combines siemcore_ai.py, iamwatch_ai.py, resurgwatch.py

import json
import time
import threading
from datetime import datetime

# === Threat DNA Correlation ===
def analyze_threat_patterns(event):
    # Simulated threat intelligence fingerprint check
    known_threats = ["CVE-2023-4567", "CVE-2024-1123"]
    for threat in known_threats:
        if threat in event.get("signature", ""):
            return True, f"Threat matched: {threat}"
    return False, "No known threat"

# === User Behavior Analytics ===
user_profiles = {}

def learn_user_behavior(user_id, action):
    profile = user_profiles.setdefault(user_id, {"logins": 0, "suspicious": 0})
    if "login" in action:
        profile["logins"] += 1
    if "suspicious" in action:
        profile["suspicious"] += 1
    user_profiles[user_id] = profile

def detect_anomaly(user_id):
    profile = user_profiles.get(user_id, {})
    if profile.get("suspicious", 0) > 3:
        return True
    return False

# === AI Event Analyzer ===
def ai_analyze_event(event):
    user = event.get("user", "unknown")
    action = event.get("action", "")
    learn_user_behavior(user, action)

    threat, reason = analyze_threat_patterns(event)
    anomaly = detect_anomaly(user)

    decision = "NORMAL"
    if threat or anomaly:
        decision = "ALERT"

    return {
        "event": event,
        "threat_match": threat,
        "anomaly_detected": anomaly,
        "decision": decision,
        "reason": reason,
        "timestamp": datetime.now().isoformat()
    }

# === Threaded AI Listener ===
def start_ai_core(event_queue):
    def run():
        while True:
            if not event_queue:
                time.sleep(1)
                continue
            event = event_queue.pop(0)
            result = ai_analyze_event(event)
            with open("logs/ai_threat_log.json", "a") as logf:
                logf.write(json.dumps(result) + "\n")
            print("[AI_CORE] Processed event:", result["decision"])
    threading.Thread(target=run, daemon=True).start()
