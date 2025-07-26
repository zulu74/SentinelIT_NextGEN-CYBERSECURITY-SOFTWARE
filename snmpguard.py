# snmpguard.py – SNMP Access Monitor with Secondary Auth

import socket
import threading
import time
from authgate import AuthGate
from sentinelIT.Eventlogger import log_event

SNMP_PORT = 161
SCAN_INTERVAL = 15  # seconds
AUTHORIZED_IPS = ["127.0.0.1"]  # Add trusted IPs if needed

class SNMPGuard:
    def __init__(self):
        self.gate = AuthGate()

    def monitor_snmp(self):
        while True:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex(("localhost", SNMP_PORT))
                    if result == 0:
                        log_event("snmpguard", f"SNMP service detected on port {SNMP_PORT}")
                        self.auth_check()
                    else:
                        print("[SNMPGuard] SNMP not active")
            except Exception as e:
                log_event("snmpguard", f"Error monitoring SNMP: {e}")
            time.sleep(SCAN_INTERVAL)

    def auth_check(self):
        print("\n[SNMPGuard] SNMP access detected. Verifying secondary auth...")
        if self.gate.authenticate("snmp"):
            print("[SNMPGuard] Access allowed")
        else:
            log_event("snmpguard", "Unauthorized SNMP access attempt blocked")
            print("[SNMPGuard] Access denied. Blocking session...")
            self.block_snmp()

    def block_snmp(self):
        # Optional: kill SNMP process or alert sysadmin
        log_event("snmpguard", "(Simulated) SNMP service shutdown")
        print("[SNMPGuard] SNMP service would be shut down here (placeholder).")


def start():
    guard = SNMPGuard()
    thread = threading.Thread(target=guard.monitor_snmp)
    thread.daemon = True
    thread.start()
    while True:
        time.sleep(60)

if __name__ == "__main__":
    start()
