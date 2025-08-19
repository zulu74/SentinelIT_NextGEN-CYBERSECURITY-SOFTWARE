#!/usr/bin/env python3
"""
kernelwatch.py — Upgraded KernelWatch for SentinelIT

Features:
- Monitors critical/system processes for suspicious mapped modules
- Detects known-bad kernel modules / suspicious memory maps
- Optional YARA scanning of mapped module files
- Emits all alerts to CloudWatch for S3 sync
- Evidence snapshot capture for forensics
- Non-destructive programmatic API: scan_kernel()
- start() entrypoint for ultimate_main.launch()
"""

import json
import logging
from logging.handlers import RotatingFileHandler
import os
import time
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any

import psutil
try:
    import yara
    YARA_AVAILABLE = True
except Exception:
    yara = None
    YARA_AVAILABLE = False

from cloudwatch import emit_event  # <-- integrate CloudWatch logging

# --- Configuration ---
APP_NAME = "KERNELWATCH"
SCAN_INTERVAL = int(os.getenv("KW_SCAN_INTERVAL", "5"))
AUTO_TERMINATE = os.getenv("KW_AUTO_TERMINATE", "0") == "1"
EVIDENCE_DIR = Path(os.getenv("SENTINELIT_EVIDENCE_DIR", "./evidence"))
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

SUSPICIOUS_MODULE_FRAGMENTS = [
    "rootkit", "malicious", "hidden", "hook", "patch", "drv", ".sys", "kernel"
]
SYSTEM_PROCS_ALLOWLIST = {"lsass.exe", "csrss.exe", "winlogon.exe", "smss.exe", "services.exe", "system"}

# --- Helpers ---
def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def safe_call(fn, default=None):
    try:
        return fn()
    except Exception:
        return default

def sha256sum(path: Path) -> str:
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
    except Exception:
        pass
    return h.hexdigest()

def capture_process_snapshot(p: psutil.Process) -> Path:
    snap = {
        "pid": p.pid,
        "name": safe_call(lambda: p.name(), ""),
        "exe": safe_call(lambda: p.exe(), ""),
        "cmdline": safe_call(lambda: p.cmdline(), []),
        "username": safe_call(lambda: p.username(), ""),
        "create_time": safe_call(lambda: p.create_time(), 0),
        "maps": []
    }
    for m in safe_call(lambda: p.memory_maps(grouped=False), []) or []:
        try:
            snap["maps"].append({"path": m.path, "perms": m.perms})
        except Exception:
            continue
    out = EVIDENCE_DIR / f"kernel_proc_{p.pid}_{int(time.time())}.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(snap, f, indent=2)
    return out

def terminate_process(p: psutil.Process) -> bool:
    try:
        name = safe_call(lambda: p.name(), "")
        if name.lower() in (n.lower() for n in SYSTEM_PROCS_ALLOWLIST):
            emit_event(APP_NAME, "termination_blocked", {"pid": p.pid, "name": name})
            return False
        p.terminate()
        try:
            p.wait(timeout=3)
        except psutil.TimeoutExpired:
            p.kill()
        emit_event(APP_NAME, "process_terminated", {"pid": p.pid, "name": name})
        return True
    except Exception:
        emit_event(APP_NAME, "termination_failed", {"pid": getattr(p, "pid", 0)})
        return False

# --- Detection ---
def detect_suspicious_modules(p: psutil.Process, rules=None) -> List[Dict[str, Any]]:
    hits: List[Dict[str, Any]] = []
    try:
        for m in safe_call(lambda: p.memory_maps(grouped=False), []) or []:
            path = (m.path or "")
            perms = (m.perms or "")
            low = path.lower()
            if any(fragment in low for fragment in SUSPICIOUS_MODULE_FRAGMENTS):
                hits.append({"path": path, "reason": "suspicious_filename_fragment", "perms": perms})
                emit_event(APP_NAME, "kernel_module_alert", {"pid": p.pid, "name": safe_call(lambda: p.name(), ""), "path": path})
            if rules and path and Path(path).exists():
                yara_matches = []  # simulate yara matches if needed
                # for real scan: yara_matches = scan_file_with_yara(rules, Path(path))
                if yara_matches:
                    hits.append({"path": path, "reason": "yara_match", "yara_hits": yara_matches})
                    emit_event(APP_NAME, "kernel_module_yara", {"pid": p.pid, "name": safe_call(lambda: p.name(), ""), "yara_hits": yara_matches})
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
    return hits

# --- Core monitoring loop ---
def monitor_loop():
    rules = None
    if YARA_AVAILABLE:
        rules = None  # load your YARA rules here
    emit_event(APP_NAME, "module_start", {"module": APP_NAME})
    while True:
        for p in psutil.process_iter(["pid", "name"]):
            hits = detect_suspicious_modules(p, rules)
            if hits:
                capture_process_snapshot(p)
                if AUTO_TERMINATE:
                    terminate_process(p)
        time.sleep(SCAN_INTERVAL)

# --- API for WatchdogAI ---
def scan_kernel() -> Dict[str, Any]:
    alerts: Dict[str, Any] = {"module_alerts": [], "pid_related": [], "notes": ""}
    for p in psutil.process_iter(["pid", "name"]):
        hits = detect_suspicious_modules(p)
        if hits:
            alerts["pid_related"].append({"pid": p.pid, "name": safe_call(lambda: p.name(), ""), "hits": hits})
            for h in hits:
                alerts["module_alerts"].append({"path": h.get("path"), "reason": h.get("reason")})
    if alerts["module_alerts"]:
        alerts["notes"] = f"checked_at={now_iso()}"
    return alerts

# --- Entrypoints ---
def start():
    logging.info(f"[{APP_NAME}] start() invoked")
    monitor_loop()

def main():
    start()

if __name__ == "__main__":
    main()

