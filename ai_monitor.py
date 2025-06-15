
import os
import smtplib
import json
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# List of critical SentinelIT modules to monitor
modules_to_monitor = [
    "main.py",
    "siemcore_ai.py",
    "iamwatch_ai.py",
    "packetshield.py",
    "policyengine.py",
    "cloudwatch.py",
    "usbwatch.py",
    "phantomstaff.py",
    "ai_monitor.py"
]

# Log file path
log_file = "logs/ai_monitor_log.json"
if not os.path.exists("logs"):
    os.makedirs("logs")

# Email configuration
email_sender = "jameszulu1574@gmail.com"
email_receiver = "jameszulu1574@gmail.com"
email_subject = "🚨 SentinelIT Module Alert"
email_password = "your-app-password-here"  # Replace with Gmail App Password

def send_email_alert(message):
    msg = MIMEMultipart()
    msg['From'] = email_sender
    msg['To'] = email_receiver
    msg['Subject'] = email_subject
    msg.attach(MIMEText(message, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_sender, email_password)
        text = msg.as_string()
        server.sendmail(email_sender, email_receiver, text)
        server.quit()
    except Exception as e:
        print(f"Email sending failed: {e}")

def check_modules():
    failures = []
    for module in modules_to_monitor:
        if not os.path.exists(module):
            failures.append(module)
    return failures

def log_issues(failed_modules):
    log_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "missing_modules": failed_modules
    }
    with open(log_file, "a") as f:
        f.write(json.dumps(log_data) + "\n")

def monitor():
    failed_modules = check_modules()
    if failed_modules:
        message = f"Alert! The following SentinelIT modules are missing or not found:\n" + "\n".join(failed_modules)
        send_email_alert(message)
        log_issues(failed_modules)
    else:
        print("✅ All SentinelIT modules are present.")

if __name__ == "__main__":
    monitor()
