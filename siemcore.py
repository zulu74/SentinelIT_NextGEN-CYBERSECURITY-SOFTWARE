def run_siemcore():
    print("[SIEMCORE] Aggregating system logs...")
    logs = [
        "User login from 10.0.0.5",
        "Firewall alert: port scan blocked",
        "Service crash: nginx exited unexpectedly"
    ]
    with open("logs/siemcore.log", "w") as f:
        for entry in logs:
            f.write(f"{entry}\n")
