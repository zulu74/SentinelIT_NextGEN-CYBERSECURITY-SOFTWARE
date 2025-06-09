import socket
import datetime

def run_scantrap():
    print("[SCANTRAP] Monitoring for Nmap-style scan patterns...")

    suspicious_flags = {
        "SYN": False,
        "FIN": False,
        "NULL": False,
        "XMAS": False
    }

    trap_ports = [22, 23, 80, 443, 445, 3389]
    log_path = "logs/scantrap.log"

    with open(log_path, "w") as log:
        for port in trap_ports:
            log.write(f"[SCANTRAP] Monitoring port {port} for scan activity\n")

        # Simulated detection (real version would use raw sockets or packet inspection)
        suspicious_flags["SYN"] = True
        suspicious_flags["XMAS"] = True

        for flag, detected in suspicious_flags.items():
            if detected:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log.write(f"[{timestamp}] Detected suspicious scan: {flag} scan\n")

    print(f"[SCANTRAP] Log saved to {log_path}")
