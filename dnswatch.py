import os
import datetime

def run_dnswatch():
    print("[DNSWATCH] Monitoring DNS queries and domain behaviors...")

    malicious_indicators = [
        "login-verify", "secure-pay", "epmm", "coldfusion", "struts",
        "zip", ".exe", "payload", "git-exploit", "base64,", "eval(",
        "sleep(30)", "<script", "ransom", "cmd.exe"
    ]

    known_malicious_ips = [
        "45.83.64.1", "185.100.87.202", "66.42.98.220", "3.121.56.55", "172.105.15.59"
    ]

    suspicious_domains = [
        "cdn-update.com", "dns-checker.org", "user-id-session.com",
        "service-login-secure.net", "config-push.systems"
    ]

    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "dnswatch_alerts.log")

    sample_dns_traffic = [
        {"domain": "login-verify-update.com", "resolved_ip": "185.100.87.202"},
        {"domain": "secure-pay.io", "resolved_ip": "172.105.15.59"},
        {"domain": "github.com", "resolved_ip": "140.82.114.3"},
        {"domain": "cdn-update.com", "resolved_ip": "45.83.64.1"},
        {"domain": "normal-site.com", "resolved_ip": "88.34.23.5"},
        {"domain": "bank.com", "resolved_ip": "3.121.56.55"}
    ]

    with open(log_path, "w", encoding="utf-8") as f:
        for entry in sample_dns_traffic:
            domain = entry["domain"]
            ip = entry["resolved_ip"]
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            for indicator in malicious_indicators:
                if indicator.lower() in domain.lower():
                    f.write(f"[{timestamp}] ⚠️ Suspicious domain keyword: {domain} contains {indicator}\n")

            if ip in known_malicious_ips:
                f.write(f"[{timestamp}] 🚨 Malicious IP detected: {ip} from {domain}\n")

            if domain in suspicious_domains:
                f.write(f"[{timestamp}] 🧠 Recon/Crawler trap: {domain} resolved to {ip}\n")

    print(f"[DNSWATCH] Scan complete. Results saved to {log_path}")
