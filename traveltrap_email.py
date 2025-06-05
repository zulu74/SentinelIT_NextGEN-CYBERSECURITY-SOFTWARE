def run_traveltrap_email():
    print("[EMAIL] Phishing alert email sent...")
    with open("logs/email_alerts.log", "w") as f:
        f.write("Phishing redirect trap alert triggered. Email sent to: James.zulu35@yahoo.co.uk\n")
