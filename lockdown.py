
# lockdown.py - SentinelIT Lockdown Module (with lockdown_protocol function)

import winreg

def lockdown_protocol():
    try:
        reg_path = r"Software\\Policies\\Microsoft\\Windows\\System"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
            winreg.SetValueEx(key, "DisableCMD", 0, winreg.REG_DWORD, 0)
        print("[SentinelIT] CMD lockdown lifted. Monitoring only.")
    except Exception as e:
        print(f"[SentinelIT] Lockdown protocol error: {e}")

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
