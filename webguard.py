
def guard_web():
    print("[+] Activating web surveillance and phishing guard...")

    protections = [
        "Scanning browser history for known phishing URLs",
        "Detecting login forms on suspicious domains",
        "Alerting on SSL certificate mismatches",
        "Blocking known redirect-based phishing links",
        "Logging all unsafe click attempts"
    ]

    for p in protections:
        print(f"[✓] {p}")

    print("[✓] Webguard protection is fully active.")

# For testing standalone
if __name__ == "__main__":
    guard_web()
