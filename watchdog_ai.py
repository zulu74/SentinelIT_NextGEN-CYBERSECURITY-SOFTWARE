
import os
import time
import datetime
import platform
import psutil

LOG_FILE = "logs/watchdog_ai.log"
CHECK_INTERVAL = 300  # every 5 minutes

modules_required = [
    "ultimate_main.py", "siemcore_ai.py", "iamwatch_ai.py", "policyengine.py",
    "cloudwatch.py", "threatdna.py", "flowtrap.py", "patternengine.py",
    "casewatch.py", "phantomstaff.py", "usbwatch.py", "yara_guardian.py"
]

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

def check_module_status():
    missing = []
    for module in modules_required:
        if not os.path.exists(module):
            missing.append(module)
    if missing:
        log(f"Missing modules: {', '.join(missing)}")
    else:
        log("All required modules are present.")

def check_performance():
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory().percent
    log(f"System CPU Usage: {cpu}%, Memory Usage: {mem}%")
    if cpu > 90 or mem > 90:
        log("WARNING: High system resource usage detected!")

def check_disk_space():
    disk = psutil.disk_usage('/')
    percent = disk.percent
    log(f"Disk Usage: {percent}%")
    if percent > 90:
        log("WARNING: Disk space critically low!")

def system_health_check():
    check_module_status()
    check_performance()
    check_disk_space()

def main():
    if not os.path.exists("logs"):
        os.makedirs("logs")
    log("Watchdog AI Monitor Started.")
    while True:
        system_health_check()
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
