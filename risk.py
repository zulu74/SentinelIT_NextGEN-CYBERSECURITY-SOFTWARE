def run_risk():
    print("[RISK] Assessing threat severity levels...")
    results = {
        "asset1": {"risk": 90, "reason": "Unpatched CVE-2023-1234"},
        "asset2": {"risk": 60, "reason": "Weak password policy"},
        "asset3": {"risk": 30, "reason": "Low exposure service"}
    }

    with open("logs/risk_report.log", "w") as f:
        for asset, info in results.items():
            line = f"{asset}: Risk Score = {info['risk']} | Reason: {info['reason']}\n"
            f.write(line)

    print("[RISK] Risk scores saved to logs/risk_report.log")
