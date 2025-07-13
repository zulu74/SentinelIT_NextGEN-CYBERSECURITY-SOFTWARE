
import psutil
import time
import logging

logging.basicConfig(filename="memory_alerts.log", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

MEMORY_THRESHOLD_PERCENT = 85

def monitor_memory(interval=5):
    while True:
        memory = psutil.virtual_memory()
        used_percent = memory.percent

        if used_percent >= MEMORY_THRESHOLD_PERCENT:
            logging.warning(f"[MEMORYWATCH] High memory usage detected: {used_percent}%")
            print(f"[MEMORYWATCH] High memory usage detected: {used_percent}%")

        time.sleep(interval)

if __name__ == "__main__":
    print("[MEMORYWATCH] Starting memory usage monitor...")
    monitor_memory()

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

