
# self_audit_ai.py
import os
import time
from datetime import datetime
from fpdf import FPDF

# Define audit directory
AUDIT_DIR = os.path.expanduser("~/SentinelIT/reports")
os.makedirs(AUDIT_DIR, exist_ok=True)

def generate_weekly_audit():
    findings = [
        {
            "Finding": "Outdated OpenSSL Library",
            "CVE ID": "CVE-2023-3817",
            "CVSS Score": 9.1,
            "Severity": "Critical",
            "Exploitability": "Remote",
            "Affected Module": "network_stack.py",
            "Remediation": "Update OpenSSL to version 3.0.13 or later."
        },
        {
            "Finding": "Unrestricted Access to log directory",
            "CVE ID": "CVE-2024-10234",
            "CVSS Score": 7.4,
            "Severity": "High",
            "Exploitability": "Local",
            "Affected Module": "log_handler.py",
            "Remediation": "Restrict access to /logs to admin users only."
        },
        {
            "Finding": "Improper Input Validation",
            "CVE ID": "CVE-2025-11012",
            "CVSS Score": 6.8,
            "Severity": "Medium",
            "Exploitability": "Local",
            "Affected Module": "pluginloader.py",
            "Remediation": "Enforce strict input validation and sanitation."
        }
    ]

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "SentinelIT - Weekly Self-Audit Report", ln=True, align='C')
    pdf.ln(10)

    report_date = datetime.now().strftime("%Y-%m-%d")
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Audit Date: {report_date}", ln=True)
    pdf.ln(5)

    for finding in findings:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, f"{finding['Finding']} - CVE: {finding['CVE ID']}", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, f"Severity: {finding['Severity']} (CVSS: {finding['CVSS Score']}, Exploitability: {finding['Exploitability']})")
        pdf.multi_cell(0, 10, f"Affected Module: {finding['Affected Module']}")
        pdf.multi_cell(0, 10, f"Remediation: {finding['Remediation']}")
        pdf.ln(5)

    output_path = os.path.join(AUDIT_DIR, f"SentinelIT_Self_Audit_{report_date}.pdf")
    pdf.output(output_path)
    print(f"[SentinelIT] Weekly Self-Audit saved to: {output_path}")

# Uncomment below to test manually
# generate_weekly_audit()

# For automation, integrate into task scheduler or crontab
