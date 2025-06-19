import time
from datetime import datetime
import random

# Simulated USB insertions
usb_events = [
    {"device": "Kingston USB", "serial": "SN-4459X", "user": "Admin", "risk": "Low"},
    {"device": "Sandisk Cruzer", "serial": "SN-9021Z", "user": "Analyst1", "risk": "Medium"},
    {"device": "Unrecognized Device", "serial": "SN-???", "user": "Unknown", "risk": "High"},
    {"device": "Lexar USB", "serial": "SN-7842L", "user": "Staff04", "risk": "Low"},
]

def start():
    print("[USBWATCH] Monitoring USB ports for activity...\n")
    for _ in range(5):
        event = random.choice(usb_events)
        print(f"[USBWATCH] Device Detected: {event['device']} | Serial: {event['serial']} | User: {event['user']} | Risk Level: {event['risk']} | Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        if event["risk"] == "High":
            print("[ALERT] High-risk USB device inserted. Initiating lockdown sequence and alert dispatch...\n")
        time.sleep(4)

if __name__ == "__main__":
    start()
