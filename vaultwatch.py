import time
import smtplib
from email.message import EmailMessage
import getpass

# List of 6 designated emails
executive_emails = [
    "exec1@example.com",
    "exec2@example.com",
    "exec3@example.com",
    "exec4@example.com",
    "exec5@example.com",
    "exec6@example.com"
]

# Dictionary to hold entered codes
entered_codes = {}

# Master pin setup (can be randomized or stored securely)
secure_pins = {
    "exec1@example.com": "135790",
    "exec2@example.com": "246801",
    "exec3@example.com": "112233",
    "exec4@example.com": "445566",
    "exec5@example.com": "778899",
    "exec6@example.com": "999000"
}

# Email alert function
def send_alert(email):
    try:
        msg = EmailMessage()
        msg.set_content(f"Vault access code requested for: {email}")
        msg["Subject"] = "SentinelIT Vault Code Access Triggered"
        msg["From"] = "vault@sentinelit.com"
        msg["To"] = email

        with smtplib.SMTP("smtp.mail.yahoo.com", 587) as server:
            server.starttls()
            server.login("vaultwatch_sentinel@yahoo.com", "yourpassword")
            server.send_message(msg)
        print(f"[+] Alert sent to {email}")
    except Exception as e:
        print(f"[!] Failed to send alert to {email}: {e}")

def start():
    print("[*] VaultWatch Security Layer Activated")
    for email in executive_emails:
        send_alert(email)
        code = getpass.getpass(prompt=f"Enter 6-digit pin for {email}: ")
        if code == secure_pins[email]:
            entered_codes[email] = code
            print(f"[+] Code accepted for {email}")
        else:
            print(f"[!] Incorrect code for {email}")
            print("[X] Triggering system lockdown for 24 hours...")
            time.sleep(3)
            return lockdown()

    if len(entered_codes) == 6:
        print("[✓] All 6 pins verified. Vault Access Granted.")

def lockdown():
    print("[*] Vault locked for 24 hours. Code red initiated.")
    time.sleep(2)
    print(">> All access denied.")
    time.sleep(1)
    exit()

# For standalone test
if __name__ == "__main__":
    start()
