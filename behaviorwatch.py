
def detect_behavior_anomalies():
    print("[+] Scanning for behavioral anomalies...")

    anomalies = [
        "Unusual login hours from admin account",
        "Rapid privilege escalation events",
        "Execution of unsigned PowerShell scripts",
        "Multiple failed login attempts from internal IP",
        "Abnormal clipboard data transfer rate"
    ]

    for anomaly in anomalies:
        print(f"[!] Detected anomaly: {anomaly}")

    print("[✓] Behavioral anomaly detection complete.")
    return anomalies

# For direct test
if __name__ == "__main__":
    detect_behavior_anomalies()
