
# iamwatch_ai.py – UEBA-Driven IAM Monitor (emoji-free)
import os
import time
import socket
import platform
import getpass
import hashlib
import json
from datetime import datetime

LOG_FILE = "iamwatch_log.txt"
MEMORY_FILE = "identity_behavior.json"

def get_identity_fingerprint():
    user = getpass.getuser()
    hostname = socket.gethostname()
    system = platform.system()
    platform_info = platform.platform()
    ip = socket.gethostbyname(hostname)
    login_time = datetime.now().strftime("%H:%M")
    device_fingerprint = f"{user}|{hostname}|{system}|{platform_info}|{ip}"
    fingerprint_hash = hashlib.sha256(device_fingerprint.encode()).hexdigest()
    return {
        "user": user,
        "ip": ip,
        "system": system,
        "platform": platform_info,
        "login_time": login_time,
        "hash": fingerprint_hash
    }

def load_behavior_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_behavior_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)

def evaluate_identity(identity, memory):
    user = identity["user"]
    login_time = identity["login_time"]
    hour = int(login_time.split(":")[0])

    if user not in memory:
        memory[user] = {
            "logins": [],
            "anomaly_score": 0,
            "flagged": False
        }

    memory[user]["logins"].append({
        "ip": identity["ip"],
        "time": login_time,
        "platform": identity["platform"]
    })

    recent_logins = memory[user]["logins"][-10:]  # Analyze last 10 logins
    anomalies = sum(1 for l in recent_logins if abs(int(l["time"].split(":")[0]) - hour) > 3)

    if anomalies >= 3:
        memory[user]["anomaly_score"] += 20
    else:
        memory[user]["anomaly_score"] = max(0, memory[user]["anomaly_score"] - 5)

    if memory[user]["anomaly_score"] >= 50:
        memory[user]["flagged"] = True

    return memory

def log_result(identity, memory):
    score = memory[identity["user"]]["anomaly_score"]
    flagged = memory[identity["user"]]["flagged"]
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        if flagged:
            f.write(f"[{now}] SUSPICIOUS: {identity['user']} from {identity['ip']} (Score={score})\n")
        else:
            f.write(f"[{now}] OK: Login by {identity['user']} from {identity['ip']} (Score={score})\n")

def main():
    print("[IAM AI] Monitoring identity behavior...")
    while True:
        identity = get_identity_fingerprint()
        memory = load_behavior_memory()
        memory = evaluate_identity(identity, memory)
        save_behavior_memory(memory)
        log_result(identity, memory)
        time.sleep(120)

if __name__ == "__main__":
    main()
