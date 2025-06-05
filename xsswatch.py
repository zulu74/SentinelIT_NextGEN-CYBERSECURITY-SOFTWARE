import os
import datetime

def run_xsswatch():
    print("[XSSWATCH] Scanning logs for blind XSS payloads...")

    log_dir = "logs"
    output_log = os.path.join(log_dir, "xsswatch_alerts.log")

    xss_indicators = ["<script", "onerror=", "src=", "eval(", "alert(", "document.cookie", "javascript:"]

    with open(output_log, "w") as out:
        for filename in os.listdir(log_dir):
            filepath = os.path.join(log_dir, filename)
            if not filename.endswith(".log") or filename == "xsswatch_alerts.log":
                continue

            with open(filepath, "r", errors="ignore") as f:
                lines = f.readlines()

            for i, line in enumerate(lines):
                for indicator in xss_indicators:
                    if indicator.lower() in line.lower():
                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        alert = f"[{timestamp}] XSS alert in {filename} (line {i+1}): {line.strip()}\n"
                        out.write(alert)

    print(f"[XSSWATCH] Scan complete. Results saved to {output_log}")
