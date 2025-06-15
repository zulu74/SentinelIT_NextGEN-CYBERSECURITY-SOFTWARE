
import yara
import os
import datetime

RULES_DIR = "rules"
SCAN_PATH = "C:\\"  # You can change this to a more focused directory
LOG_FILE = "logs/yara_guardian.log"

def log(message):
    timestamp = datetime.datetime.now().isoformat()
    with open(LOG_FILE, "a") as logf:
        logf.write(f"[{timestamp}] {message}\n")

def load_yara_rules():
    rule_files = [os.path.join(RULES_DIR, f) for f in os.listdir(RULES_DIR) if f.endswith(".yar")]
    rules = {}
    for i, file in enumerate(rule_files):
        try:
            rules[f"rule_{i}"] = yara.compile(filepath=file)
        except Exception as e:
            log(f"Failed to compile {file}: {e}")
    return rules

def scan_directory(rules):
    for root, dirs, files in os.walk(SCAN_PATH):
        for name in files:
            filepath = os.path.join(root, name)
            try:
                for rule in rules.values():
                    matches = rule.match(filepath)
                    if matches:
                        log(f"YARA match found in: {filepath} -> {matches}")
            except Exception as e:
                continue

def main():
    if not os.path.exists("logs"):
        os.makedirs("logs")
    rules = load_yara_rules()
    if rules:
        scan_directory(rules)
    else:
        log("No valid YARA rules loaded.")

if __name__ == "__main__":
    main()
