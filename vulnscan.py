# vulnscan.py – Phase 7: Vulnerability Scanner
import os
import json
import platform
import socket

def run_vulnscan():
    print("[VULNSCAN] Running offline vulnerability scan...")

    # Dummy output - in real use, connect to CVE database
    results = {
        "hostname": socket.gethostname(),
        "os": platform.system(),
        "issues": [
            {"software": "OpenSSL", "version": "1.0.2", "cve": "CVE-2023-2650"},
            {"software": "Apache", "version": "2.4.49", "cve": "CVE-2021-41773"}
        ]
    }

    os.makedirs("logs", exist_ok=True)
    with open("logs/vulnscan_results.json", "w") as f:
        json.dump(results, f, indent=4)

    print("[VULNSCAN] Scan complete. Results saved to logs/vulnscan_results.json")
