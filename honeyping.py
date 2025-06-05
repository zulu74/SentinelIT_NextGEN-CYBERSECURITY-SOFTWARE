import time
import datetime

def run_honeyping():
    print("[HONEYPING] Deploying decoy ping probes...")

    bait_messages = [
        "PING sentinel-probe01.local",
        "LOGIN admin:admin123",
        "DNS lookup for sensitive.internal",
        "FTP connection to finance-svr01"
    ]

    log_path = "logs/honeyping.log"
    with open(log_path, "w") as f:
        for msg in bait_messages:
            time.sleep(0.2)  # Simulated delay
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] Bait deployed: {msg}\n"
            f.write(log_entry)

    print(f"[HONEYPING] Decoy packets deployed. Log saved to {log_path}")
