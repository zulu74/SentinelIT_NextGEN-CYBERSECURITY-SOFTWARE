# sentinelIT.Eventlogger.py

import os
import datetime

#  Set log directory depending on platform
LOG_DIR = os.path.join("logs") if os.name == "posix" else "C:\\SentinelIT\\logs"

# Ensure the logs directory exists
os.makedirs(LOG_DIR, exist_ok=True)

def log_event(module, message, level="info"):
    """
    Logs a message with timestamp, module name, and log level.
    Output: [2025-07-02 22:17:00] [INFO] [NetWatch] Interface scan started...
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] [{level.upper()}] [{module}] {message}\n"
    log_file = os.path.join(LOG_DIR, f"{module.lower()}.log")

    try:
        with open(log_file, "a") as f:
            f.write(entry)
    except Exception as e:
        print(f"[LOGGER ERROR] Failed to write log: {e}")