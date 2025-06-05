
import json
import os
from datetime import datetime

# File locations
ASSET_FILE = "logs/asset_inventory.json"
VULN_FILE = "logs/vulnscan_results.json"
NETMAP_FILE = "logs/network_map.json"
OUTPUT_FILE = "logs/ai_threat_model.json"

# Load JSON safely
def load_json_file(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Cannot read {path}: {e}")
        return {}

# Calculate individual asset risk
def calculate_asset_risk(asset, vulns):
    score = 0
    reason = []

    # Base score for presence
    score += 10

    # Vulnerability impact
    if asset['hostname'] in vulns:
        vuln_list = vulns[asset['hostname']]
        for v in vuln_list:
            if v.get("severity") == "high":
                score += 25
                reason.append(f"High severity vuln: {v.get('id')}")
            elif v.get("severity") == "medium":
                score += 15
                reason.append(f"Medium severity vuln: {v.get('id')}")
   
    # If asset is critical or exposed in network
    if asset.get("critical", False):
        score += 20
        reason.append("Marked as critical system")

    return min(score, 100), reason

# Main model logic
def generate_threat_model():
    assets = load_json_file(ASSET_FILE).get("assets", [])
    vulns = load_json_file(VULN_FILE)
    netmap = load_json_file(NETMAP_FILE)

    report = {
        "timestamp": str(datetime.now()),
        "summary": [],
        "recommended_patches": [],
        "overall_risk_score": 0
    }

    total_score = 0
    for asset in assets:
        hostname = asset.get("hostname", "unknown")
        risk, reason = calculate_asset_risk(asset, vulns)
        total_score += risk

        # Collect patches
        patch_list = []
        if hostname in vulns:
            for v in vulns[hostname]:
                patch_list.append({
                    "id": v.get("id"),
                    "fix": v.get("patch", "Apply vendor patch")
                })

        report["summary"].append({
            "hostname": hostname,
            "ip": asset.get("ip"),
            "risk_score": risk,
            "reason": reason
        })

        if patch_list:
            report["recommended_patches"].append({
                "hostname": hostname,
                "patches": patch_list
            })

    # Average risk
    if assets:
        report["overall_risk_score"] = round(total_score / len(assets), 2)

    # Save
    with open(OUTPUT_FILE, "w") as f:
        json.dump(report, f, indent=4)

    print(f"[✓] AI Threat Model complete. Report saved to {OUTPUT_FILE}")
    if report["overall_risk_score"] >= 75:
        print("[⚠️] High system risk detected! Immediate action recommended.")

# Trigger patch logic (can be later automated)
def run_auto_patch_advice():
    print("[🔧] Placeholder: Auto patching advice system ready. Manual review required before execution.")

def run_threatmodel():
    generate_threat_model()
    run_auto_patch_advice()

if __name__ == "__main__":
    run_threatmodel() 