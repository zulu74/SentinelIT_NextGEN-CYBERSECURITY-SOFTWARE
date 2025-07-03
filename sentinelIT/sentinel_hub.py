# sentinelIT/sentinel_hub.py

from sentinelIT.Eventlogger import log_event
import threading
import importlib

MODULE_NAME = "SentinelHub"

# Centralized registry of enabled modules and their corresponding filenames (minus .py)
MODULE_REGISTRY = {
    "USBWatch": "usbwatch",
    "NetWatch": "netwatch",
    "PhantomStaff": "phantomstaff",
    "ThreatDNA": "threatdna",
    "ComplianceMonitor": "compliance_monitor"
    # Add more modules here as you build!
}

def start_module(module_key):
    module_name = MODULE_REGISTRY.get(module_key)
    if not module_name:
        log_event(MODULE_NAME, f"Module '{module_key}' not found in registry.", level="warning")
        return

    try:
        module = importlib.import_module(f"sentinelIT.{module_name}")
        thread = threading.Thread(target=module.run, name=module_key, daemon=True)
        thread.start()
        log_event(MODULE_NAME, f"Module '{module_key}' started successfully.")
    except Exception as e:
        log_event(MODULE_NAME, f"Failed to start module '{module_key}': {e}", level="error")

def start_all():
    for key in MODULE_REGISTRY:
        start_module(key)