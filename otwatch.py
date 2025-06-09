# otwatch.py - Phase 7: OT Watchdog Surveillance
import time
import logging
import random

def run_otwatch():
    print("[OTWATCH] Monitoring OT/ICS environment...")

    threats = ["PLC unauthorized command", "Modbus scan", "Unexpected I/O activity"]
    detected = random.choice([True, False])

    if detected:
        threat = random.choice(threats)
        logging.warning(f"[OTWATCH] ALERT: {threat} detected!")
        print(f"[OTWATCH] ALERT: {threat} detected!")
    else:
        print("[OTWATCH] No anomalies detected in OT/ICS systems.")

    print("[OTWATCH] Surveillance complete.")