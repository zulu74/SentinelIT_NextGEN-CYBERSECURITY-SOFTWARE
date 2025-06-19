import time
import random

def start():
    print("[SIEMCore] Module started. Correlating events...")

    patterns = [
        "Multiple failed logins",
        "Unusual port scan",
        "Privilege escalation detected",
        "Malicious executable found",
        "Suspicious DNS query",
        "Repeated access to sensitive file"
    ]

    while True:
        event = random.choice(patterns)
        print(f"[SIEM ALERT] {event}")
        time.sleep(7)
