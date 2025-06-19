import time
import random

def start():
    print("[KernelWatch] Monitoring kernel activity for rootkits or anomalies...")

    threats = [
        "Unauthorized kernel module loaded",
        "Hidden process detected",
        "Suspicious syscall interception",
        "Kernel patch anomaly",
        "Memory injection attempt"
    ]

    while True:
        alert = random.choice(threats)
        print(f"[KernelAlert] {alert}")
        time.sleep(8)
