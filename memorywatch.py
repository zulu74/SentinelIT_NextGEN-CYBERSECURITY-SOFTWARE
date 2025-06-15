
import psutil
import time
import datetime

log_file_path = "logs/memory_monitor.log"

def log(message):
    with open(log_file_path, "a") as log_file:
        timestamp = datetime.datetime.now().isoformat()
        log_file.write(f"[{timestamp}] {message}\n")

def detect_anomalous_memory_usage(threshold_percent=85):
    mem = psutil.virtual_memory()
    if mem.percent >= threshold_percent:
        log(f"High memory usage detected: {mem.percent}%")

def detect_suspicious_processes():
    suspicious_keywords = ["mimikatz", "powersploit", "meterpreter", "cobalt", "empire"]
    for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
            if any(keyword in cmdline.lower() for keyword in suspicious_keywords):
                log(f"Suspicious process detected: PID={proc.info['pid']}, CMD={cmdline}")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

def main():
    if not Path("logs").exists():
        Path("logs").mkdir()

    detect_anomalous_memory_usage()
    detect_suspicious_processes()

if __name__ == "__main__":
    main()
