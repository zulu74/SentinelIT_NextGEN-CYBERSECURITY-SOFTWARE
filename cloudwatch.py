
# cloudwatch.py – Cloud Access Anomaly Detection (SentinelIT Phase 8)
import time
import random
from datetime import datetime

LOG_FILE = "cloudwatch_log.txt"
SIMULATED_EVENTS = [
    {"user": "admin", "event": "Multiple failed API calls"},
    {"user": "guest", "event": "Access from unknown device"},
    {"user": "root", "event": "Session token replay"},
    {"user": "user1", "event": "Unusual file sync"},
    {"user": "admin", "event": "Geo-location change detected"}
]

def simulate_cloud_behavior():
    # Simulate random anomalies (for testing)
    event = random.choice(SIMULATED_EVENTS)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{now}] ALERT: {event['user']} - {event['event']}"
    with open(LOG_FILE, "a") as f:
        f.write(log_line + "\n")
    print(f"[CloudWatch] {log_line}")

def main():
    print("[CloudWatch AI] Monitoring simulated cloud activity...")
    while True:
        simulate_cloud_behavior()
        time.sleep(180)  # every 3 minutes

if __name__ == "__main__":
    main()
