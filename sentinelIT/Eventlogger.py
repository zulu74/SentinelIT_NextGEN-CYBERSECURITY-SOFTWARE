import os
import datetime

LOG_DIR = os.path.join("logs")
os.makedirs(LOG_DIR, exist_ok=True)

def log_event(module, message, level="info"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] [{level.upper()}] [{module}] {message}\n"
    log_file = os.path.join(LOG_DIR, f"{module}.log")

    try:
        with open(log_file, "a") as f:
            f.write(entry)
            f.flush()  # Make sure it writes before app exits
    except Exception:
        pass  # Don't crash the app if log write fails
