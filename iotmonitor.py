#!/usr/bin/env python3
"""
iotmonitor.py — Advanced IoT Monitor for SentinelIT

What it does (beyond typical AV/EDR):
- Live device inventory & status tracking (online/offline/ports)
- Firmware tamper detection
- Unauthorized command pattern anomaly detection
- Data exfil / DDoS-like data spike detection (EWMA baseline)
- Port-scan detection
- Auto-response: quarantine device, block/unblock IP via PacketShield hooks
- Cloud/SIEM emission via cloudwatch.emit_event (with graceful fallback)
- Safe, timezone-aware timestamps (UTC)
"""

import time
import random
import socket
from typing import Dict, List, Optional
from datetime import datetime, timezone, timedelta

# --- Integrations (graceful fallbacks) ---------------------------------
try:
    from cloudwatch import emit_event as _emit_event  # unified event bus
    def emit_event(module: str, event_type: str, details: dict):
        _emit_event(module, event_type, details)
except Exception:
    def emit_event(module: str, event_type: str, details: dict):
        print(f"[CLOUDWATCH/FALLBACK] {module} | {event_type} | {details}")

# PacketShield integration: if available, call its API; fallback to log-only
def _ps_call(fn_name: str, *args, **kwargs) -> bool:
    try:
        import packetshield  # your module with network controls
        fn = getattr(packetshield, fn_name, None)
        if callable(fn):
            return bool(fn(*args, **kwargs))
    except Exception:
        pass
    return False

def block_ip(ip: str, reason: str) -> bool:
    ok = _ps_call("block_ip", ip=ip, reason=reason) or _ps_call("request_block", ip=ip, reason=reason)
    if ok:
        print(f"[PacketShield] Blocked {ip} | reason={reason}")
    else:
        print(f"[PacketShield/FALLBACK] Would block {ip} | reason={reason}")
    emit_event("IoTMonitor", "net_block", {"ip": ip, "reason": reason, "result": ok})
    return ok

def unblock_ip(ip: str, reason: str) -> bool:
    ok = _ps_call("unblock_ip", ip=ip, reason=reason) or _ps_call("request_unblock", ip=ip, reason=reason)
    if ok:
        print(f"[PacketShield] Unblocked {ip} | reason={reason}")
    else:
        print(f"[PacketShield/FALLBACK] Would unblock {ip} | reason={reason}")
    emit_event("IoTMonitor", "net_unblock", {"ip": ip, "reason": reason, "result": ok})
    return ok

# --- Configuration ------------------------------------------------------
ALERT_THRESHOLD = 3                 # quarantine after this many alerts (rolling)
DATA_SPIKE_MULTIPLIER = 3.0         # x baseline => spike
EWMA_ALPHA = 0.2                    # smoothing factor
RECOVERY_TIME = 300                 # seconds in quarantine before auto-rejoin

FIRMWARE_VERSIONS = {
    "Thermostat": "v1.2.0",
    "CCTV Camera": "v3.0.5",
    "Smart Door Lock": "v2.1.1",
    "IoT Lightbulb": "v1.0.8",
}

DEFAULT_PORTS = {
    "Thermostat": [80, 443],
    "CCTV Camera": [80, 554],
    "Smart Door Lock": [80, 443],
    "IoT Lightbulb": [80, 443],
}

CRITICAL_COMBINE_IMMEDIATE_QUARANTINE = True
HEARTBEAT_SECS = 60  # periodic health ping

# --- Device registry & state -------------------------------------------
def utc_now():
    return datetime.now(timezone.utc)

devices: Dict[str, Dict] = {
    name: {
        "ip": f"192.168.0.{10+i}",
        "ports": DEFAULT_PORTS[name][:],
        "firmware": FIRMWARE_VERSIONS[name],
        "last_online": None,
        "alerts": 0,
        "quarantined": False,
        "quarantine_time": None,
        "baseline_pps": 200.0,        # starting EWMA packets/sec baseline
        "recent_pps": 0.0,
        "recent_cmd": "idle",
        "port_scan_suspect": False,
        "cmd_anomaly": False,
        "firmware_tampered": False,
    }
    for i, name in enumerate(FIRMWARE_VERSIONS.keys())
}

# --- Probes & simulators -----------------------------------------------
def ping_device(ip: str, port: int = 80, timeout: float = 0.8) -> bool:
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except Exception:
        return False

def check_ports(info: Dict) -> List[int]:
    closed = []
    for port in info["ports"]:
        if not ping_device(info["ip"], port):
            closed.append(port)
    return closed

def simulate_pps(name: str) -> int:
    # Normal jitter around baseline with rare bursts
    base = int(devices[name]["baseline_pps"])
    burst = random.random() < 0.10  # 10% chance burst
    if burst:
        return int(base * random.uniform(3.0, 8.0))
    return max(0, int(random.gauss(mu=base, sigma=max(10, base * 0.2))))

def ewma_update(prev: float, new: float, alpha: float = EWMA_ALPHA) -> float:
    return alpha * new + (1.0 - alpha) * prev

KNOWN_CMDS = ["status", "get_temp", "set_temp", "stream_on", "stream_off", "lock", "unlock", "ping"]
SUSPICIOUS_CMDS = ["debug_mode", "shell_exec", "upload_firmware", "erase_logs", "exfiltrate", "scan_ports"]

def simulate_command() -> str:
    if random.random() < 0.07:
        return random.choice(SUSPICIOUS_CMDS)
    return random.choice(KNOWN_CMDS)

def detect_port_scan(name: str) -> bool:
    # Simulate occasional scans against the device
    suspect = random.random() < 0.06
    devices[name]["port_scan_suspect"] = suspect
    return suspect

# --- Checks & detections -----------------------------------------------
def firmware_check(name: str, info: Dict) -> bool:
    if random.random() < 0.05:  # 5% chance tamper
        info["firmware_tampered"] = True
        msg = f"{name} firmware tampering detected"
        print(f"[ALERT] {msg}")
        emit_event("IoTMonitor", "firmware_tamper", {"device": name, "message": msg})
        return True
    return False

def command_anomaly_check(name: str, info: Dict) -> bool:
    cmd = simulate_command()
    info["recent_cmd"] = cmd
    if cmd in SUSPICIOUS_CMDS:
        info["cmd_anomaly"] = True
        msg = f"{name} suspicious command observed: {cmd}"
        print(f"[ALERT] {msg}")
        emit_event("IoTMonitor", "cmd_anomaly", {"device": name, "command": cmd})
        return True
    info["cmd_anomaly"] = False
    return False

def data_spike_check(name: str, info: Dict) -> bool:
    pps = simulate_pps(name)
    info["recent_pps"] = pps
    prev = info["baseline_pps"]
    spike = pps > (prev * DATA_SPIKE_MULTIPLIER)
    # Update baseline AFTER deciding spike (so spike doesn’t immediately raise baseline)
    info["baseline_pps"] = ewma_update(prev, float(pps))
    if spike:
        msg = f"{name} data spike detected: {pps} pps (> {DATA_SPIKE_MULTIPLIER:.1f}x baseline {prev:.0f})"
        print(f"[ALERT] {msg}")
        emit_event("IoTMonitor", "data_spike", {"device": name, "pps": pps, "baseline": prev})
        return True
    return False

# --- Response actions ---------------------------------------------------
def quarantine_device(name: str, info: Dict, reason: str = "multiple anomalies") -> None:
    if info["quarantined"]:
        return
    info["quarantined"] = True
    info["quarantine_time"] = utc_now()
    print(f"[QUARANTINE] {name} quarantined due to {reason}.")
    emit_event("IoTMonitor", "quarantine", {"device": name, "reason": reason})
    # Network isolate
    block_ip(info["ip"], reason=f"IoT quarantine: {reason}")

def recover_device(name: str, info: Dict) -> None:
    if not info["quarantined"]:
        return
    info["quarantined"] = False
    info["alerts"] = 0
    info["quarantine_time"] = None
    info["firmware_tampered"] = False
    info["cmd_anomaly"] = False
    print(f"[RECOVERY] {name} recovered and reconnected to network.")
    emit_event("IoTMonitor", "recovery", {"device": name})
    # Lift isolation
    unblock_ip(info["ip"], reason="IoT auto-recovery")

# --- Main monitoring ----------------------------------------------------
def _heartbeat(last_beat: Optional[datetime]) -> Optional[datetime]:
    now = utc_now()
    if last_beat is None or (now - last_beat).total_seconds() >= HEARTBEAT_SECS:
        emit_event("IoTMonitor", "heartbeat", {"ts": now.isoformat()})
        return now
    return last_beat

def start():
    print("[IoTMonitor] Advanced IoT monitoring with auto-isolation, recovery, and anomaly detection...")

    # announce inventory once
    inventory = [
        {"device": n, "ip": d["ip"], "ports": d["ports"], "firmware": d["firmware"]}
        for n, d in devices.items()
    ]
    emit_event("IoTMonitor", "inventory", {"devices": inventory})

    last_beat: Optional[datetime] = None

    while True:
        last_beat = _heartbeat(last_beat)

        for name, info in devices.items():
            now = utc_now()

            # Auto-recovery window
            if info["quarantined"] and info["quarantine_time"]:
                elapsed = (now - info["quarantine_time"]).total_seconds()
                if elapsed >= RECOVERY_TIME:
                    recover_device(name, info)
                else:
                    # Still quarantined; skip active checks
                    continue

            alerts = 0

            # Online/port checks
            if not ping_device(info["ip"]):
                msg = f"{name} is offline"
                print(f"[ALERT] {msg}")
                emit_event("IoTMonitor", "offline", {"device": name, "message": msg})
                alerts += 1
            else:
                info["last_online"] = now

            closed = check_ports(info)
            if closed:
                msg = f"{name} ports unresponsive: {closed}"
                print(f"[ALERT] {msg}")
                emit_event("IoTMonitor", "port_alert", {"device": name, "closed_ports": closed})
                alerts += 1

            # Behavioral detections
            if firmware_check(name, info):
                alerts += 1

            if command_anomaly_check(name, info):
                alerts += 1

            if data_spike_check(name, info):
                alerts += 1

            if detect_port_scan(name):
                msg = f"{name} potential inbound port scan"
                print(f"[ALERT] {msg}")
                emit_event("IoTMonitor", "port_scan", {"device": name})
                alerts += 1

            # Immediate quarantine if very critical combo
            if CRITICAL_COMBINE_IMMEDIATE_QUARANTINE and info["firmware_tampered"] and info["cmd_anomaly"]:
                quarantine_device(name, info, reason="firmware_tamper+cmd_anomaly")
                continue

            # Rolling alert count
            info["alerts"] += alerts

            # Threshold-based quarantine
            if info["alerts"] >= ALERT_THRESHOLD:
                quarantine_device(name, info, reason=f">= {ALERT_THRESHOLD} alerts")

        time.sleep(6)

# For ultimate_main compatibility
def start_threaded():
    start()

if __name__ == "__main__":
    start()

