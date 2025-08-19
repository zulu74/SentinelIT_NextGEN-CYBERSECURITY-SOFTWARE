#!/usr/bin/env python3
"""
memorywatch.py — Upgraded MemoryWatch for SentinelIT

- YARA scanning (optional)
- Heuristics for injection detection
- Per-process memory attribution + evidence snapshot
- Firmware baseline/verify
- SIEM JSONL + rotating logs
- Non-destructive programmatic API: scan_memory()
- start() entrypoint for ultimate_main.launch()

Environment variables:
- MW_MEMORY_THRESHOLD (int, percent) default 85
- MW_RSS_ALERT_MB (int) default 1500
- MW_SCAN_INTERVAL (seconds) default 5
- MW_FULL_SCAN (seconds) default 120
- MW_ENABLE_YARA ("1"/"0") default 1
- MW_YARA_DIR (path) default ./yara_rules
- MW_AUTO_KILL ("1"/"0") default 0
- MW_DUMP_ON_DETECT ("1"/"0") default 1
- SENTINELIT_LOG_DIR (path) default .
"""

from __future__ import annotations
import argparse
import hashlib
import json
import logging
from logging.handlers import RotatingFileHandler
import os
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import psutil

# Optional yara
try:
    import yara  # type: ignore
    YARA_AVAILABLE = True
except Exception:
    yara = None
    YARA_AVAILABLE = False

# --- Config ------------------------------------------------------------
APP_NAME = "MEMORYWATCH"
LOG_DIR = Path(os.getenv("SENTINELIT_LOG_DIR", "."))
LOG_FILE = LOG_DIR / "memory_alerts.log"
SIEM_EVENT_FILE = LOG_DIR / "siem_events.jsonl"
EVIDENCE_DIR = Path(os.getenv("SENTINELIT_EVIDENCE_DIR", "./evidence"))
FIRMWARE_BASELINE = Path(os.getenv("SENTINELIT_FW_BASELINE", "./firmware_baseline.json"))

LOG_DIR.mkdir(parents=True, exist_ok=True)
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

MEMORY_THRESHOLD_PERCENT = int(os.getenv("MW_MEMORY_THRESHOLD", "85"))
PROCESS_RSS_ALERT_MB = int(os.getenv("MW_RSS_ALERT_MB", "1500"))
SCAN_INTERVAL_SECONDS = int(os.getenv("MW_SCAN_INTERVAL", "5"))
PERIODIC_FULL_SCAN_SECONDS = int(os.getenv("MW_FULL_SCAN", "120"))

ENABLE_YARA = os.getenv("MW_ENABLE_YARA", "1") == "1"
YARA_RULES_DIR = Path(os.getenv("MW_YARA_DIR", "./yara_rules"))
YARA_TIMEOUT_MS = int(os.getenv("MW_YARA_TIMEOUT_MS", "200"))

CAPTURE_PROC_DUMP = os.getenv("MW_DUMP_ON_DETECT", "1") == "1"
MAX_DUMP_BYTES = int(os.getenv("MW_MAX_DUMP", "10485760"))

AUTO_KILL_KNOWN_BAD = os.getenv("MW_AUTO_KILL", "0") == "1"
AUTO_ISOLATE_ON_SERIOUS = os.getenv("MW_AUTO_ISOLATE", "0") == "1"

SUSPICIOUS_TREES = [
    ("powershell.exe", "msbuild.exe"),
    ("powershell.exe", "rundll32.exe"),
    ("winword.exe", "powershell.exe"),
    ("excel.exe", "powershell.exe"),
    ("wscript.exe", "powershell.exe"),
    ("cmd.exe", "powershell.exe"),
    ("python.exe", "rundll32.exe"),
]

RISKY_BINARIES = {"rundll32.exe", "mshta.exe", "regsvr32.exe", "installutil.exe", "wmic.exe", "certutil.exe"}

# --- Logging -----------------------------------------------------------
def setup_logging() -> None:
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(LOG_FILE, maxBytes=2_000_000, backupCount=5)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    logger.addHandler(console)

# --- SIEM emitter ------------------------------------------------------
def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def siem_emit(event: Dict) -> None:
    event["ts"] = now_iso()
    event["app"] = APP_NAME
    try:
        with open(SIEM_EVENT_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, default=str) + "\n")
    except Exception as e:
        logging.error(f"[SIEM] Failed to write event: {e}")

# --- Firmware baseline/verify -----------------------------------------
def firmware_paths() -> List[Path]:
    paths: List[Path] = []
    system = platform.system().lower()
    if system == "windows":
        candidates = [
            Path(r"C:\\Windows\\Boot\\EFI\\bootmgfw.efi"),
            Path(r"C:\\Windows\\System32\\winload.efi"),
        ]
        paths.extend([p for p in candidates if p.exists()])
    elif system == "linux":
        boot = Path("/boot")
        efi = Path("/boot/efi")
        for root in [boot, efi]:
            if root.exists():
                for p in root.rglob("*.efi"):
                    paths.append(p)
                for p in root.rglob("vmlinuz*"):
                    paths.append(p)
                for p in root.rglob("grub*"):
                    if p.is_file():
                        paths.append(p)
    else:
        logging.warning("[FW] Firmware baseline not supported on this OS.")
    return paths

def sha256sum(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def firmware_baseline() -> None:
    entries = {}
    for p in firmware_paths():
        try:
            entries[str(p)] = {"sha256": sha256sum(p), "size": p.stat().st_size}
        except Exception as e:
            logging.warning(f"[FW] Unable to hash {p}: {e}")
    with open(FIRMWARE_BASELINE, "w", encoding="utf-8") as f:
        json.dump({"created": now_iso(), "entries": entries}, f, indent=2)
    logging.info(f"[FW] Firmware baseline saved to {FIRMWARE_BASELINE}")

def firmware_verify() -> List[Tuple[str, str, str]]:
    if not FIRMWARE_BASELINE.exists():
        logging.warning("[FW] Baseline not found. Run --baseline-firmware first.")
        return []
    with open(FIRMWARE_BASELINE, "r", encoding="utf-8") as f:
        data = json.load(f)
    findings: List[Tuple[str, str, str]] = []
    for path_str, meta in data.get("entries", {}).items():
        p = Path(path_str)
        if not p.exists():
            findings.append((path_str, "missing", meta.get("sha256", "")))
            continue
        try:
            cur = sha256sum(p)
            if cur != meta.get("sha256"):
                findings.append((path_str, "hash_mismatch", cur))
        except Exception as e:
            logging.warning(f"[FW] Unable to hash {p}: {e}")
    if findings:
        for path_str, kind, cur in findings:
            msg = f"[FW] Firmware integrity alert: {path_str} -> {kind}"
            logging.error(msg)
            siem_emit({"type": "firmware_integrity", "path": path_str, "issue": kind, "current": cur})
    else:
        logging.info("[FW] Firmware verified: no changes detected.")
    return findings

# --- YARA compilation & scanning --------------------------------------
def compile_yara_rules() -> Optional["yara.Rules"]:
    if not ENABLE_YARA or not YARA_AVAILABLE:
        return None
    if not YARA_RULES_DIR.exists():
        logging.warning(f"[YARA] Rules dir not found: {YARA_RULES_DIR}")
        return None
    sources = {}
    for i, p in enumerate(sorted(YARA_RULES_DIR.rglob("*.yar*"))):
        try:
            sources[f"r{i}"] = p.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            logging.warning(f"[YARA] Could not read {p}: {e}")
    if not sources:
        logging.warning("[YARA] No rule files discovered.")
        return None
    try:
        rules = yara.compile(sources=sources)
        logging.info(f"[YARA] Compiled {len(sources)} rule sources.")
        return rules
    except Exception as e:
        logging.error(f"[YARA] Compilation failed: {e}")
        return None

def scan_file_with_yara(rules, path: Path) -> List[Dict]:
    findings = []
    if not path.exists() or not path.is_file():
        return findings
    try:
        matches = rules.match(filepath=str(path), timeout=YARA_TIMEOUT_MS)
        for m in matches:
            findings.append({"rule": m.rule, "tags": list(m.tags), "meta": dict(m.meta)})
    except Exception as e:
        logging.debug(f"[YARA] Scan error on {path}: {e}")
    return findings

# --- Process inspection helpers ----------------------------------------
def short_exe(p: psutil.Process) -> str:
    try:
        return os.path.basename(p.exe())
    except Exception:
        try:
            return p.name()
        except Exception:
            return f"pid:{p.pid}"

def safe_call(fn, default):
    try:
        return fn()
    except Exception:
        return default

def asdict_mem(mem) -> Dict:
    if not mem:
        return {}
    return {
        "rss": getattr(mem, "rss", 0),
        "vms": getattr(mem, "vms", 0),
        "shared": getattr(mem, "shared", 0),
        "text": getattr(mem, "text", 0),
        "data": getattr(mem, "data", 0),
        "dirty": getattr(mem, "dirty", 0),
    }

def looks_injected(p: psutil.Process) -> bool:
    try:
        for m in p.memory_maps(grouped=False):
            path = (m.path or "").lower()
            perms = (m.perms or "")
            if "x" in perms and (path == "" or path.startswith("[anon") or path == "<anonymous>"):
                return True
    except Exception:
        pass
    return False

def risky_tree(p: psutil.Process) -> Optional[Tuple[str, str]]:
    try:
        parent = p.parent()
        if not parent:
            return None
        a = short_exe(parent).lower()
        b = short_exe(p).lower()
        for x, y in SUSPICIOUS_TREES:
            if a == x and b == y:
                return (a, b)
    except Exception:
        return None
    return None

def highlight_lolbin(p: psutil.Process) -> bool:
    try:
        return short_exe(p).lower() in RISKY_BINARIES
    except Exception:
        return False

def capture_proc_snapshot(p: psutil.Process) -> Path:
    snap = {
        "pid": p.pid,
        "ppid": safe_call(lambda: p.ppid(), None),
        "name": short_exe(p),
        "cmdline": safe_call(lambda: p.cmdline(), []),
        "username": safe_call(lambda: p.username(), ""),
        "create_time": safe_call(lambda: p.create_time(), 0),
        "connections": [
            {
                "laddr": f"{c.laddr.ip}:{c.laddr.port}" if c.laddr else None,
                "raddr": f"{c.raddr.ip}:{c.raddr.port}" if c.raddr else None,
                "status": c.status,
            }
            for c in safe_call(lambda: p.connections(kind="inet"), [])
        ],
        "memory_info": asdict_mem(safe_call(lambda: p.memory_info(), None)),
        "maps": [
            {"path": m.path, "perms": m.perms, "rss": getattr(m, "rss", 0)}
            for m in safe_call(lambda: p.memory_maps(grouped=False), [])
        ],
    }
    out = EVIDENCE_DIR / f"proc_{p.pid}_{int(time.time())}.json"
    try:
        with open(out, "w", encoding="utf-8") as f:
            json.dump(snap, f, indent=2)
    except Exception:
        logging.exception("[EVIDENCE] Failed to write snapshot")
    return out

def dump_process_memory(p: psutil.Process) -> Optional[Path]:
    try:
        out_dir = EVIDENCE_DIR / f"dump_{p.pid}_{int(time.time())}"
        out_dir.mkdir(parents=True, exist_ok=True)
        paths = set()
        exe = safe_call(lambda: Path(p.exe()), None)
        if exe and exe.exists():
            paths.add(exe)
        for m in safe_call(lambda: p.memory_maps(grouped=False), []):
            if m.path and os.path.isabs(m.path):
                paths.add(Path(m.path))
        dumped = 0
        for src in paths:
            try:
                tgt = out_dir / src.name
                with open(src, "rb") as fsrc, open(tgt, "wb") as fdst:
                    while True:
                        chunk = fsrc.read(1024 * 1024)
                        if not chunk:
                            break
                        fdst.write(chunk)
                        dumped += len(chunk)
                        if dumped >= MAX_DUMP_BYTES:
                            logging.info(f"[EVIDENCE] Dump size cap reached ({MAX_DUMP_BYTES} bytes)")
                            break
            except Exception:
                continue
        return out_dir
    except Exception as e:
        logging.debug(f"[EVIDENCE] Dump failed: {e}")
        return None

# --- Response actions ---------------------------------------------------
def isolate_host() -> None:
    logging.critical("[IR] Host isolation requested (not implemented).")
    siem_emit({"type": "host_isolation", "result": "requested"})

def kill_process(p: psutil.Process) -> bool:
    try:
        p.terminate()
        try:
            p.wait(timeout=3)
        except psutil.TimeoutExpired:
            p.kill()
        logging.warning(f"[IR] Process terminated: pid={p.pid} name={short_exe(p)}")
        siem_emit({"type": "process_kill", "pid": p.pid, "name": short_exe(p)})
        return True
    except Exception as e:
        logging.error(f"[IR] Failed to kill pid {p.pid}: {e}")
        return False

def notify_phantomstaff(message: str) -> None:
    try:
        phantom = __import__("phantomstaff")
        fn = getattr(phantom, "notify_phantomstaff", None) or getattr(phantom, "start", None)
        if callable(fn):
            try:
                fn(message)
            except Exception:
                logging.exception("[PHANTOM] phantom call failed")
    except Exception:
        logging.info(f"[PHANTOM][FALLBACK] {message}")

# --- Core monitoring loop ---------------------------------------------
def monitor_loop() -> None:
    rules = compile_yara_rules()
    last_full = 0.0
    logging.info(f"[{APP_NAME}] Starting monitor | TH={MEMORY_THRESHOLD_PERCENT}% | YARA={'on' if rules else 'off'}")

    while True:
        try:
            vmem = psutil.virtual_memory()
            used_percent = int(vmem.percent)
            if used_percent >= MEMORY_THRESHOLD_PERCENT:
                msg = f"[{APP_NAME}] High memory usage detected: {used_percent}%"
                logging.warning(msg)
                siem_emit({"type": "memory_pressure", "percent": used_percent})

            for p in psutil.process_iter(["pid", "name"]):
                try:
                    mem_info = p.memory_info()
                    rss_mb = int(mem_info.rss / (1024 * 1024))

                    injected = looks_injected(p)
                    risky = risky_tree(p)
                    lolbin = highlight_lolbin(p)

                    if rss_mb >= PROCESS_RSS_ALERT_MB or injected or risky or lolbin:
                        event = {
                            "type": "process_alert",
                            "pid": p.pid,
                            "name": short_exe(p),
                            "rss_mb": rss_mb,
                            "injected": injected,
                            "risky_tree": risky,
                            "lolbin": lolbin,
                        }
                        logging.error(f"[{APP_NAME}] Alert: {event}")
                        siem_emit(event)

                        snap = capture_proc_snapshot(p)
                        logging.info(f"[EVIDENCE] Snapshot -> {snap}")

                        if CAPTURE_PROC_DUMP:
                            dump_dir = dump_process_memory(p)
                            if dump_dir:
                                logging.info(f"[EVIDENCE] Dumped files -> {dump_dir}")

                        yara_hits: List[Dict] = []
                        if rules:
                            exe_path = safe_call(lambda: Path(p.exe()), None)
                            if exe_path:
                                yara_hits.extend(scan_file_with_yara(rules, exe_path))
                            for m in safe_call(lambda: p.memory_maps(grouped=False), []):
                                if m.path and os.path.isabs(m.path):
                                    yara_hits.extend(scan_file_with_yara(rules, Path(m.path)))
                            if yara_hits:
                                logging.error(f"[YARA] Matches for pid {p.pid}: {yara_hits}")
                                siem_emit({"type": "yara_match", "pid": p.pid, "hits": yara_hits})

                        if AUTO_KILL_KNOWN_BAD and (injected or (yara_hits)):
                            kill_process(p)
                            notify_phantomstaff(f"Terminated suspicious process {short_exe(p)} ({p.pid})")

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            now = time.time()
            if now - last_full >= PERIODIC_FULL_SCAN_SECONDS:
                last_full = now
                fw_findings = firmware_verify()
                if fw_findings and AUTO_ISOLATE_ON_SERIOUS:
                    isolate_host()

            time.sleep(SCAN_INTERVAL_SECONDS)

        except KeyboardInterrupt:
            logging.info(f"[{APP_NAME}] Stopping monitor (Ctrl+C)")
            break
        except Exception as e:
            logging.exception(f"[{APP_NAME}] Loop error: {e}")
            time.sleep(2)

# --- Programmatic scan API for WatchdogAI -------------------------------
def scan_memory() -> Optional[Dict]:
    """
    Lightweight programmatic scan API for WatchdogAI.
    Returns None when nothing suspicious, or a dict:
      { "pid_hits": [pid,...], "paths": [...], "yara_hits":[...], "notes": "..." }
    Non-destructive — no termination or quarantine performed here.
    """
    try:
        findings: Dict = {"pid_hits": [], "paths": [], "yara_hits": [], "notes": ""}
        rules = compile_yara_rules()
        vmem = psutil.virtual_memory()
        findings["notes"] = f"vmem_percent={int(vmem.percent)}"
        for p in psutil.process_iter(["pid", "name"]):
            try:
                mem_info = safe_call(lambda: p.memory_info(), None)
                rss_mb = int(mem_info.rss / (1024 * 1024)) if mem_info else 0
                injected = looks_injected(p)
                risky = risky_tree(p)
                lolbin = highlight_lolbin(p)
                if rss_mb >= PROCESS_RSS_ALERT_MB or injected or risky or lolbin:
                    findings["pid_hits"].append(p.pid)
                    exe = safe_call(lambda: p.exe(), None)
                    if exe:
                        findings["paths"].append(str(exe))
                    if rules and exe:
                        yara_hits = scan_file_with_yara(rules, Path(exe))
                        if yara_hits:
                            findings["yara_hits"].extend(yara_hits)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if findings["pid_hits"] or findings["yara_hits"]:
            return findings
        return None
    except Exception:
        logging.exception("scan_memory failed")
        return None

# --- CLI/entrypoints -----------------------------------------------------
def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="SentinelIT MemoryWatch (upgraded)")
    ap.add_argument("--baseline-firmware", action="store_true", help="Create/overwrite firmware baseline hashes")
    ap.add_argument("--verify-firmware", action="store_true", help="Verify against firmware baseline and exit")
    ap.add_argument("--once", action="store_true", help="Run a single monitor iteration then exit")
    return ap.parse_args()

def start():
    """Entry for ultimate_main.launch()"""
    setup_logging()
    logging.info(f"[{APP_NAME}] start() invoked")
    siem_emit({"type": "module_start", "module": APP_NAME})
    monitor_loop()

def main() -> None:
    setup_logging()
    args = parse_args()

    if args.baseline_firmware:
        firmware_baseline()
        return
    if args.verify_firmware:
        firmware_verify()
        return

    if args.once:
        try:
            vmem = psutil.virtual_memory()
            used_percent = int(vmem.percent)
            if used_percent >= MEMORY_THRESHOLD_PERCENT:
                logging.warning(f"[{APP_NAME}] High memory usage detected: {used_percent}%")
                siem_emit({"type": "memory_pressure", "percent": used_percent})
        except Exception as e:
            logging.error(f"[{APP_NAME}] One-shot failed: {e}")
        return

    monitor_loop()

if __name__ == "__main__":
    main()
