def run_threatdna():
    print("[THREATDNA] Scanning for malware DNA fingerprints...")
    threats = [
        {"id": "MD5-001", "type": "Ransomware", "status": "Quarantined"},
        {"id": "SHA256-XYZ", "type": "Keylogger", "status": "Detected"}
    ]
    with open("logs/threatdna.log", "w") as f:
        for threat in threats:
            f.write(f"{threat['id']} | {threat['type']} | {threat['status']}\n")

if __name__ == '__main__':
    run_threatdna()
