
import os
import psutil
import socket
from datetime import datetime

LOG_FILE = "logs/cloudwatch.log"
SOC_QUEUE = "logs/soc_queue.json"
WATCHED_PROCESSES = ["Dropbox.exe", "GoogleDriveFS.exe", "OneDrive.exe", "Box.exe"]
CLOUD_DOMAINS = ["dropbox.com", "drive.google.com", "onedrive.live.com", "icloud.com", "s3.amazonaws.com"]

def log_event(event, score=50):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {event}\n"
    with open(LOG_FILE, "a") as log:
        log.write(log_entry)

    # Simulate sending to SOCWatch
    soc_event = {
        "incident_id": f"SOC-{timestamp.replace(':', '').replace(' ', '')}-Cloud",
        "module": "cloudwatch",
        "event": event,
        "risk_score": score,
        "timestamp": timestamp
    }

    try:
        import json
        if os.path.exists(SOC_QUEUE):
            with open(SOC_QUEUE, "r") as f:
                data = json.load(f)
        else:
            data = []

        data.append(soc_event)
        with open(SOC_QUEUE, "w") as f:
            json.dump(data, f, indent=4)

    except Exception as e:
        log_event(f"Error updating SOC queue: {e}")

def check_cloud_sync_processes():
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] in WATCHED_PROCESSES:
            log_event(f"Cloud sync process detected: {proc.info['name']} (PID {proc.pid})", score=70)

def run_cloudwatch():
    log_event("CloudWatch started.")
    check_cloud_sync_processes()

if __name__ == "__main__":
    run_cloudwatch()
