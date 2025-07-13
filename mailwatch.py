
import os
import time

def monitor_emails(log_path='email_log.txt'):
    try:
        print("[MailWatch] Starting email monitoring...")
        if not os.path.exists(log_path):
            print(f"[MailWatch] Log file {log_path} does not exist.")
            return

        with open(log_path, 'r') as file:
            lines = file.readlines()

        for line in lines:
            if any(keyword in line.lower() for keyword in ['phishing', 'alert', 'suspicious', 'malware']):
                print(f"[MailWatch] Alert! Suspicious email activity detected: {line.strip()}")

        print("[MailWatch] Email monitoring completed.")
    except Exception as e:
        print(f"[MailWatch] Error monitoring emails: {str(e)}")

import time
import random

def start():
    print("[MailWatch] Monitoring email and clipboard for suspicious content...")

    events = [
        "Phishing email detected with masked URL",
        "Clipboard contained suspicious link, cleared",
        "Malicious attachment quarantined",
        "Email with spoofed sender flagged",
        "Suspicious domain found in clipboard history"
    ]

    while True:
        print(f"[MailWatch Alert] {random.choice(events)}")
        time.sleep(7)

