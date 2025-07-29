# threatreport1.py - Tracks attacks per computer in SentinelIT

from datetime import datetime
import random

# Simulated list of registered computers (numbered 1 to 1000)
computers = [f"Computer-{i}" for i in range(1, 1001)]

# Attack types with categories (severity to be determined by analysis logic)
attack_types = [
    ("SQL Injection", "Application"),
    ("TCP Flood", "Network"),
    ("XSS Attempt", "Application"),
    ("Unauthorized Access", "Application"),
    ("UDP Flood", "Network"),
    ("Phishing Payload", "Email"),
    ("DNS Flood", "Network"),
    ("RDP Brute Force", "Remote Access"),
    ("PowerShell Obfuscation", "Behavioral"),
    ("Malicious USB Activity", "Device")
]

# Temporary simulated severity classifier
def determine_severity(attack_type):
    high_risk = ["SQL Injection", "Unauthorized Access", "Phishing Payload", "RDP Brute Force", "Malicious USB Activity"]
    medium_risk = ["TCP Flood", "UDP Flood", "PowerShell Obfuscation"]
    low_risk = ["XSS Attempt", "DNS Flood"]

    if attack_type in high_risk:
        return "High"
    elif attack_type in medium_risk:
        return "Medium"
    else:
        return "Low"

def generate_computer_threats():
    threats = []
    for _ in range(10):
        computer = random.choice(computers)
        attack, vector = random.choice(attack_types)
        severity = determine_severity(attack)
        threats.append({
            "computer": computer,
            "attack_type": attack,
            "vector": vector,
            "severity": severity,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    return threats

# 🔥 Run and show simulated output
if __name__ == "__main__":
    threats = generate_computer_threats()
    for t in threats:
        print(t)

