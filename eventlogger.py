import logging
import os
from datetime import datetime

# Configuration
LOG_DIR = "/usr/sentinelIT/logs"
DATESTAMP = datetime.now().strftime('%Y-%m-%d')
LOG_FILE = os.path.join(LOG_DIR, f"sentinelIT_{DATESTAMP}.log")

# Ensure the logs directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

def log_event(module: str, event: str, level: str = "info"):
    """
    Log an event with a given module name and severity level.
    :param module: Name of the SentinelIT submodule reporting the event
    :param event: Description of the event
    :param level: Logging level (info, warning, error, debug)
    """
    message = f"[{module.upper()}] {event}"
    level = level.lower()
    if level == "info":
        logging.info(message)
    elif level == "warning":
        logging.warning(message)
    elif level == "error":
        logging.error(message)
    elif level == "debug":
        logging.debug(message)
    else:
        logging.info(f"[UNKNOWN LEVEL] {message}")