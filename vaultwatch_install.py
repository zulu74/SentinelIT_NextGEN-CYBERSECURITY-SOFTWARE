
import json

CONFIG_FILE = "vault_config.json"
LOG_FILE = "vault_log.txt"

def log_event(message):
    with open(LOG_FILE, "a") as log:
        log.write(f"{time.ctime()} - {message}\n")

def save_config(data):
    with open(CONFIG_FILE, "w") as config:
        json.dump(data, config)

def install_vault():
    print("🔐 First-Time Installation – Set Up 6 Officials with PINs and Emails")
    vault_data = {"officials": {}}

    for i in range(1, 7):
        while True:
            pin = input(f"Enter 6-digit PIN for Official {i}: ").strip()
            if pin.isdigit() and len(pin) == 6:
                break
            print("❌ Invalid PIN. Must be 6 digits.")

        email = input(f"Enter email address for Official {i}: ").strip()
        vault_data["officials"][str(i)] = {"email": email, "pin": pin}

    save_config(vault_data)
    log_event("✅ Initial Vault Configuration Completed")
    print("✅ Vault has been successfully installed and configured.")

if __name__ == "__main__":
    install_vault()
