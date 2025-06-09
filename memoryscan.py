
import random
import time

def scan_memory():
    print("[+] Scanning system memory for malicious patterns...")

    findings = [
        "Suspicious code injection in svchost.exe",
        "Encoded payload found in notepad.exe memory",
        "Injected DLL with hidden entry point",
        "Shellcode signature matched in msedge.exe"
    ]

    for finding in findings:
        if random.choice([True, False]):
            print(f"[!] Memory anomaly: {finding}")
        else:
            print(f"[-] Clean segment: {finding}")
        time.sleep(0.3)

    print("[✓] Memory scan completed.")
    return findings

# For test run
if __name__ == "__main__":
    scan_memory()
