
import json
import time
import random

def monitor_iam_events():
    print("[IAMWatch AI] Monitoring Identity and Access Management activities...")
    alerts = []

    dummy_events = [
        {"user": "admin", "action": "login", "location": "South Africa", "time": "03:12"},
        {"user": "guest", "action": "attempted_privilege_escalation", "location": "USA", "time": "15:40"},
        {"user": "internal", "action": "multiple_failed_logins", "location": "UK", "time": "12:22"},
        {"user": "external", "action": "login_successful", "location": "Germany", "time": "18:55"},
        {"user": "admin", "action": "unusual_ip_login", "location": "Singapore", "time": "05:03"}
    ]

    selected = random.sample(dummy_events, 3)
    for event in selected:
        if "privilege_escalation" in event["action"] or "failed_logins" in event["action"] or "unusual_ip_login" in event["action"]:
            alerts.append({
                "alert": "Suspicious IAM activity detected",
                "user": event["user"],
                "action": event["action"],
                "location": event["location"],
                "time": event["time"]
            })

    return alerts

if __name__ == "__main__":
    result = monitor_iam_events()
    print(json.dumps(result, indent=2))
