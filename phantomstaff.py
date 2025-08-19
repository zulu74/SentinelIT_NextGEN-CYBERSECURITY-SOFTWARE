# phantomstaff.py - SentinelIT AI Security & Staff Monitoring (Integrated)

import datetime
import logging
import json
import os
import random
import time
from pathlib import Path
from typing import List, Dict, Any

# --- Import SentinelIT modules ---
import memorywatch
import kernelwatch
import usbwatch

# --- Configuration ---
LOG_DIR = Path(os.getenv("SENTINELIT_LOG_DIR", "./logs"))
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "phantomstaff.log"
SIEM_EVENT_FILE = LOG_DIR / "phantom_events.jsonl"

ALERT_LEVELS = ["INFO", "WARNING", "CRITICAL"]

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

STAFF_EVENTS = [
    "Password reset requested by staff ID 001",
    "Unauthorized login detected for staff ID 105",
    "Helpdesk query: VPN not connecting",
    "Security alert: Silent duress trigger from reception",
    "Access attempt blocked: Invalid staff clearance level"
]

# --- Helper Functions ---

def log_event(message: str, level: str = "INFO") -> None:
    level = level.upper()
    if level not in ALERT_LEVELS:
        level = "INFO"
    print(f"[PHANTOMSTAFF] {level}: {message}")
    getattr(logging, level.lower())(message)
    siem_emit({"level": level, "message": message})

def siem_emit(event: Dict[str, Any]) -> None:
    event["ts"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        with open(SIEM_EVENT_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
    except Exception as e:
        logging.error(f"[SIEM] Failed to write event: {e}")

# --- Event Aggregation ---

def aggregate_module_events() -> List[Dict[str, Any]]:
    events = []

    # MemoryWatch: check for injected or risky processes
    for proc in memorywatch.psutil.process_iter(["pid", "name"]):
        try:
            injected = memorywatch.looks_injected(proc)
            risky = memorywatch.risky_tree(proc)
            lolbin = memorywatch.highlight_lolbin(proc)
            if injected or risky or lolbin:
                events.append({
                    "level": "CRITICAL" if injected else "WARNING",
                    "message": f"MemoryWatch alert: {proc.pid}:{proc.name()} | injected={injected} risky={risky} lolbin={lolbin}"
                })
        except (memorywatch.psutil.NoSuchProcess, memorywatch.psutil.AccessDenied):
            continue

    # KernelWatch: detect monitored process anomalies
    for proc in kernelwatch.psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] in kernelwatch.MONITORED_PROCESSES:
                files = proc.open_files()
                if files:
                    events.append({
                        "level": "CRITICAL",
                        "message": f"KernelWatch alert: PID={proc.pid} Name={proc.info['name']} opened files unexpectedly"
                    })
        except (kernelwatch.psutil.NoSuchProcess, kernelwatch.psutil.AccessDenied):
            continue

    # USBWatch: simulate alerts for unknown devices
    usb_alerts = usbwatch.scan_usb_devices() if hasattr(usbwatch, "scan_usb_devices") else []
    for alert in usb_alerts:
        events.append(alert)

    return events

# --- Core PhantomStaff Loop ---

def start():
    log_event("PhantomStaff AI Helpdesk & Security Monitoring initialized.", "INFO")
    last_yara_reload = 0

    while True:
        # Emit staff/system events
        event = random.choice(STAFF_EVENTS)
        log_event(event, "INFO")

        # Aggregate module events
        module_events = aggregate_module_events()
        for mevent in module_events:
            log_event(mevent["message"], mevent["level"])

        # AI Suggestions
        advice = random.choice([
            "Review high memory processes.",
            "Verify firmware integrity immediately.",
            "Check recent USB activity for suspicious files.",
            "Ensure multi-factor authentication is enforced.",
            "Investigate unexpected kernel file access."
        ])
        log_event(f"AI Suggestion: {advice}", "INFO")

        # Periodically reload YARA rules
        now = time.time()
        if now - last_yara_reload > 120:
            last_yara_reload = now
            if memorywatch.ENABLE_YARA:
                rules = memorywatch.compile_yara_rules()
                if rules:
                    log_event(f"YARA rules reloaded ({len(rules.rules)} rules).", "INFO")
                else:
                    log_event("No YARA rules found or compilation failed.", "WARNING")

        time.sleep(7)

# --- CLI Entry ---
if __name__ == "__main__":
    start()
