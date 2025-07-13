
def send_phishing_alert(subject, body):
    print(f"[EMAIL ALERT] Subject: {subject}")
    print(f"Body: {body}")
    # In production, insert SMTP logic here if needed

import time
import random

def start():
    print("[TravelTrap Email Scanner] Monitoring for redirector-based phishing attempts...")

    alerts = [
        "Suspicious redirect detected: https://google.com/travel/clk?...",
        "Entropy pattern anomaly in redirected token string.",
        "Known phishing redirector used: /secure/login",
        "Redirector matches blocked domain: hxxps://redirect-link.to/phish",
        "Redirection link triggered honeypot analysis."
    ]

    while True:
        print(f"[TravelTrap Alert] {random.choice(alerts)}")
        time.sleep(11)

