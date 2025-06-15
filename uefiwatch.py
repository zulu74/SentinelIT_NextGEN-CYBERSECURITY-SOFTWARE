
import os
import hashlib
import datetime
import subprocess

def log(message):
    with open("logs/uefi_bios_tamper.log", "a") as log_file:
        timestamp = datetime.datetime.now().isoformat()
        log_file.write(f"[{timestamp}] {message}\n")

def get_bios_info():
    try:
        result = subprocess.check_output("wmic bios get smbiosbiosversion,serialnumber", shell=True)
        return result.decode()
    except Exception as e:
        return str(e)

def get_uefi_boot_order():
    try:
        result = subprocess.check_output("bcdedit /enum firmware", shell=True)
        return result.decode()
    except Exception as e:
        return str(e)

def hash_firmware_values(value):
    return hashlib.sha256(value.encode()).hexdigest()

def main():
    bios_data = get_bios_info()
    uefi_data = get_uefi_boot_order()
    bios_hash = hash_firmware_values(bios_data)
    uefi_hash = hash_firmware_values(uefi_data)

    baseline_bios = "baseline_bios.hash"
    baseline_uefi = "baseline_uefi.hash"

    if not os.path.exists("logs"):
        os.makedirs("logs")

    if not os.path.exists(baseline_bios) or not os.path.exists(baseline_uefi):
        with open(baseline_bios, "w") as f:
            f.write(bios_hash)
        with open(baseline_uefi, "w") as f:
            f.write(uefi_hash)
        log("Baseline firmware hash created.")
    else:
        with open(baseline_bios, "r") as f:
            if f.read().strip() != bios_hash:
                log("BIOS tampering detected!")

        with open(baseline_uefi, "r") as f:
            if f.read().strip() != uefi_hash:
                log("UEFI boot order tampering detected!")

if __name__ == "__main__":
    main()
