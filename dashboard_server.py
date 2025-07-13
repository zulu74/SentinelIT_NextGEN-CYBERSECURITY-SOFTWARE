
import time

def run_dashboard():
    print("[DASHBOARD] Starting SentinelIT Dashboard...")
    # Simulated dashboard server loop
    while True:
        print("[DASHBOARD] Running dashboard service...")
        time.sleep(10)

import time
import random

def start():
    print("[DashboardServer] Launching SentinelIT Dashboard...")

    services = ["SIEMCore", "IoTMonitor", "KernelWatch", "MemoryWatch", "VaultWatch", "PowerWatch"]
    status = ["Running", "Idle", "Scanning", "Blocked Threat", "Paused"]

    while True:
        service = random.choice(services)
        stat = random.choice(status)
        print(f"[Dashboard] {service} Status: {stat}")
        time.sleep(5)
