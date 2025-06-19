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
