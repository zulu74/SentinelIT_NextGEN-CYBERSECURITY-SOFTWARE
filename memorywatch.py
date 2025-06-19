import time
import random

def start():
    print("[MemoryWatch] Scanning memory for injections and tampering...")

    anomalies = [
        "DLL injection attempt",
        "Suspicious memory allocation",
        "Memory corruption detected",
        "Hidden process payload",
        "Heap spray behavior"
    ]

    while True:
        alert = random.choice(anomalies)
        print(f"[MemoryAlert] {alert}")
        time.sleep(7)
