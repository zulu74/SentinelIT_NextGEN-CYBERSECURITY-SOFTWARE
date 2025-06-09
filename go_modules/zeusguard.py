
import os
import time

def detect_zeus_activity():
    print("[+] Scanning for Zeus malware signatures...")

    # Simulated Zeus indicators
    suspicious_paths = [
        "C:\\Windows\\System32\\sdra64.exe",
        "C:\\Users\\Public\\ZeusLogs\\logs.txt",
        "C:\\ProgramData\\randomname.exe"
    ]

    detected = []

    for path in suspicious_paths:
        if os.path.exists(path):
            print(f"[!] Zeus indicator found: {path}")
            detected.append(path)
        else:
            print(f"[-] Clean: {path}")

    if not detected:
        print("[✓] No Zeus activity detected.")
    else:
        print(f"[!] {len(detected)} potential Zeus indicators found.")

    return detected

# Standalone test
if __name__ == "__main__":
    detect_zeus_activity()
