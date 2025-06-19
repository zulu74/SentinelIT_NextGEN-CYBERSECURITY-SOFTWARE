import time
import random

def start():
    print("[IoTMonitor] Monitoring IoT devices for anomalies...")

    devices = ["Thermostat", "CCTV Camera", "Smart Door Lock", "IoT Lightbulb"]
    alerts = ["offline", "firmware tampering", "unauthorized command", "data spike", "port scan detected"]

    while True:
        device = random.choice(devices)
        alert = random.choice(alerts)
        print(f"[ALERT] {device}: {alert}")
        time.sleep(6)
