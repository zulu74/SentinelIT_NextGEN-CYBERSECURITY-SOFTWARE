
import json
import time
from getpass import getpass

CONFIG_FILE = "vault_config.json"
LOG_FILE = "vault_log.txt"

def log_event(message):
    with open(LOG_FILE, "a") as log:
        log.write(f"{time.ctime()} - {message}\n")

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

def reboot_vault():
    print("🔁 SYSTEM REBOOT INITIATED – 24 HOURS EXPIRED")
    config = load_config()
    officials = config["officials"]

    success_count = 0
    missing_index = None

    for i in range(1, 7):
        index = str(i)
        input_code = input(f"Official {index} – Enter your 6-digit PIN: ").strip()
        if input_code == officials[index]["pin"]:
            print("✅ Verified")
            success_count += 1
        else:
            print(f"⚠️ PIN incorrect or user unavailable for Official {index}")
            missing_index = index

    if success_count == 6:
        print("🔓 All Officials Verified – Vault is active again.")
        log_event("✅ Vault rebooted successfully – all 6 verified")
    elif success_count == 5 and missing_index:
        print("🛡️ 1 Official unavailable – you may re-register their passcode.")
        email = input(f"Enter new email for Official {missing_index}: ").strip()
        while True:
            new_pin = input(f"Enter new 6-digit PIN for Official {missing_index}: ").strip()
            if new_pin.isdigit() and len(new_pin) == 6:
                break
            print("❌ Invalid PIN. Must be 6 digits.")

        officials[missing_index] = {"email": email, "pin": new_pin}
        save_config(config)
        print("✅ New Official registered. Vault rebooted and secured.")
        log_event(f"🔁 New Official {missing_index} registered and vault rebooted")
    else:
        print("❌ More than one Official missing – Vault remains locked.")
        log_event("⛔ Vault reboot failed – insufficient verification")

if __name__ == "__main__":
    reboot_vault()
