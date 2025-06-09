
import os
import time

def scan_with_clamav():
    print("[+] Starting ClamAV scan simulation...")

    files_to_scan = [
        "C:/Users/Public/test1.exe",
        "C:/ProgramData/suspicious.dll",
        "C:/Temp/injection_payload.vbs"
    ]

    for file in files_to_scan:
        print(f"[✓] Scanning: {file}")
        time.sleep(0.5)
        print(f"[-] No threat found in {file}")

    print("[✓] ClamAV scan completed. No threats detected.")

# For standalone test
if __name__ == "__main__":
    scan_with_clamav()
