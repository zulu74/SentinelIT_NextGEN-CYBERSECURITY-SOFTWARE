
import time
import json
import smtplib
from email.message import EmailMessage
from getpass import getpass

CONFIG_FILE = "vault_config.json"
LOG_FILE = "vault_log.txt"

def log_event(message):
    with open(LOG_FILE, "a") as log:
        log.write(f"{time.ctime()} - {message}\n")

def load_config():
    with open(CONFIG_FILE, "r") as config:
        return json.load(config)

def send_code_red_emails(officials, smtp_config):
    for i, data in officials.items():
        msg = EmailMessage()
        msg['Subject'] = "🚨 CODE RED: Unauthorized Vault Access Attempt"
        msg['From'] = smtp_config['sender']
        msg['To'] = data['email']
        msg.set_content("An unauthorized attempt to access the secure vault has been detected.\n"
                        "The system has triggered CODE RED and is locked for 24 hours.")

        try:
            with smtplib.SMTP_SSL(smtp_config['server'], smtp_config['port']) as smtp:
                smtp.login(smtp_config['sender'], smtp_config['password'])
                smtp.send_message(msg)
            print(f"📧 Alert sent to {data['email']}")
        except Exception as e:
            log_event(f"❌ Failed to send Code Red email to {data['email']}: {str(e)}")

def ai_detect_anomaly(code_sequence):
    if len(set(code_sequence)) < 6:
        log_event("⚠️ AI DETECTED DUPLICATE OR PATTERNED ENTRIES")
        return True
    if any(code == "000000" or code == "123456" for code in code_sequence):
        log_event("⚠️ AI DETECTED GENERIC OR WEAK PASSCODES")
        return True
    return False

def start_vault_sequence():
    config = load_config()
    officials = config["officials"]

    print("🔐 Vault Access Sequence Started")
    smtp_config = {
        "server": input("SMTP Server (e.g., smtp.gmail.com): "),
        "port": int(input("SMTP Port (e.g., 465): ")),
        "sender": input("Sender Email: "),
        "password": getpass("Sender Email Password: ")
    }

    code_sequence = []
    start_time = time.time()

    for i in range(1, 7):
        elapsed = time.time() - start_time
        if elapsed > 30:
            log_event("⛔ TIMEOUT – Code Red Triggered")
            send_code_red_emails(officials, smtp_config)
            return print("🚨 CODE RED ACTIVATED")

        input_code = input(f"Enter 6-digit passcode for Official {i}: ").strip()
        code_sequence.append(input_code)

        if input_code != officials[str(i)]["pin"]:
            log_event(f"❌ WRONG CODE – Official {i}")
            send_code_red_emails(officials, smtp_config)
            return print("🚨 CODE RED ACTIVATED")

        print("✅ Code Accepted")
        time.sleep(5)

    if ai_detect_anomaly(code_sequence):
        send_code_red_emails(officials, smtp_config)
        return print("🚨 CODE RED ACTIVATED BY AI ANOMALY DETECTION")

    print("🔓 Vault Access Granted")
    log_event("✅ VAULT UNLOCKED – All 6 Codes Verified")

if __name__ == "__main__":
    start_vault_sequence()
