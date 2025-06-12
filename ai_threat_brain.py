
# ai_threat_brain.py
import hashlib
import time
from datetime import datetime

THREAT_LOG = "logs/ai_threat_correlation.log"

def correlate_threat(event_type, details, severity=3):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    threat_id = hashlib.sha256((event_type + details + timestamp).encode()).hexdigest()[:12]
    score = severity * 25  # Convert to 0-100 scale
    threat_entry = f"[{timestamp}] THREAT ID: {threat_id} | TYPE: {event_type} | SEVERITY: {severity} | SCORE: {score} | DETAILS: {details}\n"

    with open(THREAT_LOG, "a") as log:
        log.write(threat_entry)

    return {
        "id": threat_id,
        "score": score,
        "severity": severity,
        "timestamp": timestamp,
        "details": details
    }

# Example usage
if __name__ == "__main__":
    sample = correlate_threat("HONEYPOT_TRIGGER", "RDP honeypot activated by IP 192.168.0.55", severity=4)
    print("Threat Correlated:", sample)
