import json
import datetime
import os

def run_policyengine():
    print("[POLICYENGINE] Enforcing compliance policy mappings...")

    # Try to load latest detections from logs/detections.json
    detection_file = "logs/detections.json"
    if os.path.exists(detection_file):
        with open(detection_file, "r", encoding="utf-8") as f:
            detections = json.load(f)
        print("[POLICYENGINE] Loaded detections from logs/detections.json")
    else:
        # fallback simulated values
        detections = {
            "xsswatch": True,
            "dnswatch": True,
            "threatdna": True,
            "risk": True,
            "otwatch": False
        }
        print("[POLICYENGINE] No detection file found, using fallback data.")

    # Define compliance mappings
    policies = {
        "ISO 27001": ["threatdna", "risk", "xsswatch"],
        "NIST 800-53": ["risk", "dnswatch", "otwatch"],
        "GDPR": ["xsswatch", "dnswatch"],
        "HIPAA": ["risk", "dnswatch"],
        "PCI DSS": ["xsswatch", "threatdna"],
        "COBIT": ["risk", "threatdna", "dnswatch"]
    }

    policy_results = {}
    for policy, modules in policies.items():
        # Which modules are failing compliance
        non_compliant = [mod for mod in modules if detections.get(mod, False)]
        total_checks = len(modules)
        passed = total_checks - len(non_compliant)
        compliance_score = round((passed / total_checks) * 100, 2)

        policy_results[policy] = {
            "required_modules": modules,
            "non_compliant_modules": non_compliant,
            "status": "NON-COMPLIANT" if non_compliant else "COMPLIANT",
            "compliance_score": compliance_score
        }

        # Real-time alert for critical policies
        if policy in ["ISO 27001", "NIST 800-53", "GDPR"] and non_compliant:
            print(f"[ALERT] {policy} is NON-COMPLIANT! Issues: {', '.join(non_compliant)}")

    # Build final report
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report = {
        "timestamp": timestamp,
        "policy_assessment": policy_results
    }

    # Save main report
    os.makedirs("logs", exist_ok=True)
    with open("logs/policy_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Append to history file
    history_file = "logs/policy_history.json"
    history = []
    if os.path.exists(history_file):
        with open(history_file, "r", encoding="utf-8") as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = []
    history.append(report)
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

    print(f"[POLICYENGINE] Policy audit complete. Report saved to logs/policy_report.json")
    print(f"[POLICYENGINE] History updated in logs/policy_history.json")


