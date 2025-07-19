import os
import time
import socket
import json
import datetime
import getpass
import subprocess

# === Configuration ===
LOG_DIR = os.path.expanduser("~/sentinelit/web_logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "web_traffic_log.json")
INTERVAL_SECONDS = 60  # adjust as needed

def resolve_ip(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except:
        return None

def capture_connections():
    visited_sites = []

    # Use netstat to capture network connections
    if os.name == 'nt':
        command = 'netstat -nob'
    else:
        command = 'netstat -tunp'

    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.DEVNULL).decode(errors="ignore")
        lines = output.splitlines()

        for line in lines:
            if "ESTABLISHED" in line or "SYN_SENT" in line:
                parts = line.split()
                remote = parts[2] if os.name == 'nt' else parts[4]
                ip = remote.split(':')[0]

                if ip.startswith("127.") or ip.startswith("::1") or ip.startswith("0.") or len(ip) < 7:
                    continue  # skip local or invalid

                hostname = resolve_ip(ip)
                if hostname and any(ext in hostname for ext in ['.com', '.org', '.net', '.co', '.io']):
                    visited_sites.append({
                        "timestamp": datetime.datetime.now().isoformat(),
                        "user": getpass.getuser(),
                        "ip": ip,
                        "domain": hostname
                    })

        return visited_sites
    except Exception as e:
        print(f"[WebTracker] Error scanning connections: {e}")
        return []

def save_logs(entries):
    if not entries:
        return

    # Load existing logs
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try:
                existing = json.load(f)
            except:
                existing = []
    else:
        existing = []

    # Append new entries and write
    existing.extend(entries)
    with open(LOG_FILE, "w") as f:
        json.dump(existing, f, indent=4)

    print(f"[WebTracker] Logged {len(entries)} new site(s)")

def start_tracking():
    print("[WebTracker] Website tracking started... Monitoring every", INTERVAL_SECONDS, "seconds.")
    while True:
        entries = capture_connections()
        save_logs(entries)
        time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    start_tracking()
