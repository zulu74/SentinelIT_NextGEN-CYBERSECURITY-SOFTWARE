
import psutil
import logging
import time
import os

LOG_FILE = "kernelwatch_log.txt"
MONITORED_PROCESSES = ["lsass.exe", "csrss.exe", "winlogon.exe", "smss.exe"]

logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format="%(asctime)s [KERNELWATCH] %(message)s")

def log_suspicious_activity(pid, name):
    logging.warning(f"Suspicious process interaction detected: PID={pid}, Name={name}")

def monitor_kernel_processes():
    logging.info("KernelWatch started monitoring...")
    while True:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] in MONITORED_PROCESSES:
                    open_files = proc.open_files()
                    if open_files:
                        log_suspicious_activity(proc.info['pid'], proc.info['name'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        time.sleep(5)

if __name__ == "__main__":
    monitor_kernel_processes()

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

