import os
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

AUTHORIZED_SENDERS = ["admin@example.com"]
ALERT_RECEIVER = "james.zulu35@yahoo.co.uk"
SMTP_SERVER = "smtp.mail.yahoo.com"
SMTP_PORT = 587
SMTP_USERNAME = "james.zulu35@yahoo.co.uk"
SMTP_PASSWORD = "your_app_password_here"  # Replace with app password

def send_email_alert(drive):
    msg = MIMEMultipart()
    msg['From'] = SMTP_USERNAME
    msg['To'] = ALERT_RECEIVER
    msg['Subject'] = f"USB Alert: USB Drive {drive} Detected"

    body = f"A USB drive ({drive}) was connected to the workstation."
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"[USBWATCH] Email alert sent for USB drive {drive}")
    except Exception as e:
        print(f"[USBWATCH] Failed to send email: {e}")

def monitor_usb():
    print("[USBWATCH] Monitoring for USB devices...")
    initial_drives = set(os.popen("wmic logicaldisk get caption").read().split())
    while True:
        time.sleep(5)
        current_drives = set(os.popen("wmic logicaldisk get caption").read().split())
        new_drives = current_drives - initial_drives
        if new_drives:
            for drive in new_drives:
                if drive.startswith("A:") or drive.startswith("B:"):
                    continue
                print(f"[USBWATCH] USB drive {drive} detected.")
                send_email_alert(drive)
            initial_drives = current_drives