
# ai_speed_monitor.py - SentinelIT AI Performance Booster and System Monitor

import psutil
import threading
import time
import logging
import platform

logging.basicConfig(filename='system_health_log.txt', level=logging.INFO)

def monitor_performance():
    while True:
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent

        logging.info(f"CPU: {cpu}% | Memory: {memory}% | Disk: {disk}%")

        if cpu > 90 or memory > 90:
            logging.warning("[AI BOOSTER] High usage detected. Optimizing processes...")
            # Placeholder: trigger lightweight resource cleanup or alert
        time.sleep(10)

def optimize_startup_speed():
    # Lightweight simulation of startup tuning (expandable)
    print("[AI BOOSTER] Optimizing SentinelIT processing priority...")
    p = psutil.Process()
    try:
        if platform.system() == "Windows":
            p.nice(psutil.HIGH_PRIORITY_CLASS)
        else:
            p.nice(-10)
        logging.info("Process priority elevated for AI boost.")
    except Exception as e:
        logging.warning(f"Priority change failed: {e}")

def main():
    print("[SentinelIT AI BOOSTER] Engaged.")
    optimize_startup_speed()
    threading.Thread(target=monitor_performance, daemon=True).start()

if __name__ == "__main__":
    main()
