import time
import random

def start():
    print("[PowerWatch] Monitoring power sources: Solar (Primary), Generator, and Electricity (Fallback)...")

    power_events = [
        "Solar input stable. Running on primary power.",
        "Grid power fluctuation detected. Switching to generator.",
        "Generator maintenance required within 48 hours.",
        "Unauthorized power cut attempt blocked – lockdown triggered.",
        "All power sources synchronized and secure."
    ]

    while True:
        print(f"[PowerWatch Status] {random.choice(power_events)}")
        time.sleep(10)
