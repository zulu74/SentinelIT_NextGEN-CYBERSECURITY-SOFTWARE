
import json
import time
import random

def analyze_logs(log_entries):
    alerts = []
    for entry in log_entries:
        if "unauthorized" in entry.lower() or "failed login" in entry.lower():
            alerts.append({
                "type": "Unauthorized Access Attempt",
                "details": entry,
                "severity": "High"
            })
        elif "malware" in entry.lower() or "ransomware" in entry.lower():
            alerts.append({
                "type": "Malware Detection",
                "details": entry,
                "severity": "Critical"
            })
        elif "cmd" in entry.lower() or "powershell" in entry.lower():
            alerts.append({
                "type": "Suspicious Command Activity",
                "details": entry,
                "severity": "Medium"
            })
    return alerts

def simulate_siem_activity():
    dummy_logs = [
        "Unauthorized access attempt from IP 192.168.1.12",
        "Failed login to admin portal",
        "PowerShell executed suspicious command",
        "Detected malware in C:\\Users\\Public\\update.exe",
        "Normal traffic from endpoint 10.0.0.5",
        "CMD command executed: net user admin"
    ]
    selected_logs = random.sample(dummy_logs, 3)
    results = analyze_logs(selected_logs)
    print("[SIEMCore AI] Log entries analyzed. Alerts generated:")
    for alert in results:
        print(json.dumps(alert, indent=2))
    return results

if __name__ == "__main__":
    simulate_siem_activity()
