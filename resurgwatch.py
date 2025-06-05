"""
resurgwatch.py – Resurgent Exploit Logic Pattern Detection
Powered by SentinelIT Threat Memory Engine
"""

import os
import json
import hashlib

RESURGENCE_DB = "resurg_patterns.json"

# Load known exploit logic patterns
def load_patterns():
    if not os.path.exists(RESURGENCE_DB):
        print("[ResurgWatch] No resurgence pattern database found.")
        return []
    with open(RESURGENCE_DB, "r") as f:
        return json.load(f)

# Generate a simple behavior fingerprint of file content
def fingerprint_code(file_path):
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read().lower()
        # Create a behavior pattern (keywords present)
        return {
            "length": len(content),
            "sha256": hashlib.sha256(content.encode()).hexdigest(),
            "keywords": [kw for kw in COMMON_KEYWORDS if kw in content]
        }
    except Exception as e:
        print(f"[ResurgWatch] Error analyzing {file_path}: {e}")
        return {}

# Compare a new file to known exploit logic
def detect_resurgence(file_path, patterns):
    fingerprint = fingerprint_code(file_path)
    matches = []
    for pattern in patterns:
        score = len(set(pattern["resurgence_keywords"]) & set(fingerprint.get("keywords", []))) / len(pattern["resurgence_keywords"])
        if score >= pattern.get("ai_weight", 0.9):
            matches.append((pattern["cve"], score))
    return matches

# Example common exploit terms (can be expanded)
COMMON_KEYWORDS = [
    "mshta", "powershell", "vbs", "macro", "jndi", "ldap", "winword",
    "script", "cmd", "calc.exe", "shell", "eval", "base64", "autoopen"
]

# Example run method
def run_resurgwatch():
    patterns = load_patterns()
    target_dir = "suspicious_scripts"
    if not os.path.exists(target_dir):
        print("[ResurgWatch] No 'suspicious_scripts' directory found.")
        return
    for file in os.listdir(target_dir):
        if file.endswith(".py") or file.endswith(".vbs") or file.endswith(".txt"):
            full_path = os.path.join(target_dir, file)
            result = detect_resurgence(full_path, patterns)
            if result:
                for match in result:
                    print(f"[ALERT] File {file} resembles {match[0]} with similarity score {match[1]:.2f}")
            else:
                print(f"[OK] {file} shows no resurgent logic.")

if __name__ == "__main__":
    run_resurgwatch()
