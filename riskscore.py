# riskscore.py – Phase 7: Risk Scoring Engine

import json
import os

def calculate_risk_score(threats):
    score = 0
    for threat in threats:
        score += threat.get("severity", 0)
    return min(score, 100)

def run_riskscore():
    print("[RISK] Assessing threat severity levels...")
    
    threats = [
        {"id": "CVE-2024-2221", "severity": 30},
        {"id": "CVE-2023-3374", "severity": 45},
        {"id": "CISA-KNOWN", "severity": 20}
    ]

    risk_score = calculate_risk_score(threats)

    os.makedirs("logs", exist_ok=True)
    with open("logs/risk_score.json", "w") as f:
        json.dump({
            "total_score": risk_score,
            "threats_analyzed": threats
        }, f, indent=4)

    print(f"[RISK] Overall system risk score: {risk_score}")