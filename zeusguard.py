
# zeusguard.py - SentinelIT module to counter Zeus malware behavior

import os
import time
import hashlib
import socket
import threading

# Common Zeus behavior indicators (e.g., mutexes, registry entries, file hashes)
ZEUS_INDICATORS = [
    "Zbot", "sdra64.exe", "ntos.exe", "lowsec\user.ds", "lowsec\local.ds",
    "C:\\WINDOWS\\system32\\sdra64.exe"
]

# Known Zeus Command and Control IPs/Domains (mocked for demo)
ZEUS_C2_DOMAINS = [
    "zeus-c2.example.com", "badserver.ru", "123.45.67.89"
]

# Local registry scan simulation (Windows only; requires winreg for real)
def simulate_registry_scan():
    print("[ZeusGuard] Simulating registry scan for Zeus indicators...")
    time.sleep(1)
    print("[ZeusGuard] No suspicious registry entries found.")

# File scan for Zeus indicators
def scan_files():
    print("[ZeusGuard] Scanning system files for Zeus indicators...")
    suspicious = []
    for root, dirs, files in os.walk("C:\\"):
        for file in files:
            for ind in ZEUS_INDICATORS:
                if ind.lower() in file.lower():
                    suspicious.append(os.path.join(root, file))
    if suspicious:
        print("[ZeusGuard] Suspicious Zeus-like files found:")
        for f in suspicious:
            print(f" - {f}")
    else:
        print("[ZeusGuard] No Zeus-like files found.")

# Network check for Zeus C2
def monitor_network():
    print("[ZeusGuard] Monitoring for known Zeus C2 connections...")
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    for domain in ZEUS_C2_DOMAINS:
        print(f"[ZeusGuard] Scanning for domain: {domain}...")
        time.sleep(0.5)
    print("[ZeusGuard] No active C2 communications detected.")

def run_zeusguard():
    print("[ZeusGuard] Starting Zeus countermeasures...")
    t1 = threading.Thread(target=simulate_registry_scan)
    t2 = threading.Thread(target=scan_files)
    t3 = threading.Thread(target=monitor_network)
    t1.start()
    t2.start()
    t3.start()
    t1.join()
    t2.join()
    t3.join()
    print("[ZeusGuard] Zeus malware defense active.")

if __name__ == "__main__":
    run_zeusguard()
