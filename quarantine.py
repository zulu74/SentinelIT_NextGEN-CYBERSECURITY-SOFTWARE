
import os
import shutil
from datetime import datetime

def isolate_threats(file_paths):
    quarantine_dir = "C:\\ProgramData\\SentinelIT_Quarantine"
    os.makedirs(quarantine_dir, exist_ok=True)

    log_file = os.path.join(quarantine_dir, "quarantine_log.txt")
    with open(log_file, "a") as log:
        for path in file_paths:
            if os.path.exists(path):
                try:
                    filename = os.path.basename(path)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    new_name = f"{timestamp}_{filename}"
                    target = os.path.join(quarantine_dir, new_name)
                    shutil.move(path, target)
                    log.write(f"[{timestamp}] Moved: {path} -> {target}\n")
                    print(f"[+] Quarantined: {path}")
                except Exception as e:
                    print(f"[!] Failed to quarantine {path}: {e}")
            else:
                print(f"[!] File not found: {path}")

# For direct test
if __name__ == "__main__":
    test_files = ["C:\\Users\\Public\\malware_sample.exe"]
    isolate_threats(test_files)
