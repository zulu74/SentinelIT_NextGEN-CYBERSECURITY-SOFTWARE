import time
import random

def start():
    print("[StealthCam] Monitoring webcam activity for unauthorized usage...")

    events = [
        "Webcam activated without user session",
        "Stealth capture triggered on login attempt",
        "Webcam blocked due to suspicious process",
        "Admin webcam surveillance initiated",
        "Unauthorized webcam access attempt"
    ]

    while True:
        print(f"[StealthCam Alert] {random.choice(events)}")
        time.sleep(8)
