import os
import json
import datetime
import threading
import smtplib
from email.message import EmailMessage

from sentinelIT.Eventlogger import log_event

MODULE_NAME = "ComplianceMonitor"
REPORT_DIR = "reports/soc2"
ADMIN_FILE = "verified_admins.json"
WEEKLY_INTERVAL = 60 * 60 * 24 * 7  # 7 days

def load_verified_admins():
    try:
        with open(ADMIN_FILE, "r") as f:
            return json.load(f).get("recipients", [])
    except FileNotFoundError:
        return []

def generate_audit_log():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    week_id = datetime.datetime.now().strftime("%Y-W%U")
    report_data = {
        "timestamp": timestamp,
        "week": week_id,
        "threats_detected": 0,
        "threats_neutralized": 0,
        "config_changes": [],
        "cves_resolved": [],
        "staff_activity": []
    }

    os.makedirs(os.path.join(REPORT_DIR, week_id), exist_ok=True)
    filepath = os.path.join(REPORT_DIR, week_id, "report.json")

    with open(filepath, "w") as f:
        json.dump(report_data, f, indent=4)

    log_event(MODULE_NAME, f"Weekly compliance report generated: {filepath}")
    return filepath

def email_report(report_path, recipients):
    try:
        msg = EmailMessage()
        msg["Subject"] = "SentinelIT: Weekly SOC 2 Compliance Report"
        msg["From"] = "noreply@sentinelit.local"
        msg["To"] = ", ".join(recipients)

        with open(report_path, "rb") as f:
            msg.add_attachment(f.read(), maintype="application", subtype="json", filename=os.path.basename(report_path))

        # Configure your SMTP settings here:
        with smtplib.SMTP("localhost") as server:
            server.send_message(msg)

        log_event(MODULE_NAME, f"Compliance report emailed to: {', '.join(recipients)}")

    except Exception as e:
        log_event(MODULE_NAME, f"Email dispatch failed: {e}", level="warning")

def generate_and_dispatch():
    recipients = load_verified_admins()
    if not recipients:
        log_event(MODULE_NAME, "No verified admin recipients found.")
        return

    report_path = generate_audit_log()
    email_report(report_path, recipients)

def schedule_next_run():
    threading.Timer(WEEKLY_INTERVAL, run).start()

def run():
    log_event(MODULE_NAME, "Compliance Monitor started.")
    generate_and_dispatch()
    schedule_next_run()