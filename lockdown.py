import time

def start():
    print("[Lockdown] Monitoring CMD and PowerShell access...")

    blocked_actions = [
        "Unauthorized CMD access blocked",
        "PowerShell session terminated",
        "Execution policy breach detected",
        "CMD lockdown triggered by policy",
        "Alert: Repeated PowerShell launch attempts"
    ]

    while True:
        for action in blocked_actions:
            print(f"[Lockdown Alert] {action}")
            time.sleep(5)
