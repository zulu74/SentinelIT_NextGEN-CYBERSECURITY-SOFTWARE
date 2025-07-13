import time
import json
import smtplib
from email.message import EmailMessage
from getpass import getpass

LOG_FILE = "vault_log.txt"

# ---------- Executive Profiles ----------
executives = [
    {
        "name": "Exec One",
        "email": "exec1@example.com",
        "role": "CISO",
        "pin": "135790"
    },
    {
        "name": "Exec Two",
        "email": "exec2@example.com",
        "role": "CTO",
        "pin": "246801"
    },
    {
        "name": "Exec Three",
        "email": "exec3@example.com",
        "role": "CSO",
        "pin": "112233"
    },
    {
        "name": "Exec Four",
        "email": "exec4@example.com",
        "role": "COO",
        "pin": "445566"
    },
    {
        "name": "Exec Five",
        "email": "exec5@example.com",
        "role": "CEO",
        "pin": "778899"
    },
    {
        "name": "Exec Six",
        "email": "exec6@example.com",
        "role": "Board",
        "pin": "999888"
    }
]

# ---------- Logging ----------
def log_event(message):
    with open(LOG_FILE, "a") as log:
        log.write(f"{time.ctime()} - {message}\n")

# ---------- Email Alerts ----------
def send_alerts(smtp_config, message):
    for exec in executives:
        alert = EmailMessage()
        alert['Subject'] = "🚨 CODE RED: Unauthorized Vault Access"
        alert['From'] = smtp_config['sender']
        alert['To'] = exec['email']
        alert.set_content(message)
        try:
            with smtplib.SMTP_SSL(smtp_config['server'], smtp_config['port']) as smtp:
                smtp.login(smtp_config['sender'], smtp_config['password'])
                smtp.send_message(alert)
            print(f"📧 Alert sent to {exec['email']}")
        except Exception as e:
            log_event(f"❌ Failed to send alert to {exec['email']}: {str(e)}")

# ---------- AI Passcode Analysis ----------
def ai_detect_anomaly(code_sequence):
    if len(set(code_sequence)) < 6:
        log_event("⚠️ AI DETECTED DUPLICATE OR PATTERNED ENTRIES")
        return True
    if any(code in ["000000", "123456"] for code in code_sequence):
        log_event("⚠️ AI DETECTED GENERIC OR WEAK PASSCODES")
        return True
    return False

# ---------- Vault Access Logic ----------
def start_vault_sequence():
    print("🔐 Vault Access Sequence Started")

    smtp_config = {
        "server": input("SMTP Server (e.g., smtp.gmail.com): "),
        "port": int(input("SMTP Port (e.g., 465): ")),
        "sender": input("Sender Email: "),
        "password": getpass("Sender Email Password: ")
    }

    code_sequence = []
    start_time = time.time()

    for exec in executives:
        elapsed = time.time() - start_time
        if elapsed > 30:
            log_event("⛔ TIMEOUT – Code Red Triggered")
            send_alerts(smtp_config, "Vault access timed out. CODE RED initiated.")
            return print("🚨 CODE RED ACTIVATED")

        input_code = input(f"Enter 6-digit passcode for {exec['name']} ({exec['role']}): ").strip()
        code_sequence.append(input_code)

        if input_code != exec['pin']:
            log_event(f"❌ WRONG CODE – {exec['name']} ({exec['email']})")
            send_alerts(smtp_config, f"Wrong code detected for {exec['name']}. Vault locked.")
            return print("🚨 CODE RED ACTIVATED")

        print("✅ Code Accepted")
        time.sleep(3)

    if ai_detect_anomaly(code_sequence):
        send_alerts(smtp_config, "AI anomaly detected in passcode sequence. Vault locked.")
        return print("🚨 CODE RED ACTIVATED BY AI")

    print("🔓 Vault Access Granted")
    log_event("✅ VAULT UNLOCKED – All codes verified")

# ---------- Entry Point ----------
if __name__ == "__main__":
    start_vault_sequence()