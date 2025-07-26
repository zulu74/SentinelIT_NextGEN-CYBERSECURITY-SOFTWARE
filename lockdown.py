# lockdown.py – SentinelIT Lockdown Module (Fixed for ultimate_main compatibility)

import winreg
import time
from sentinelIT.Eventlogger import log_event

def lockdown_protocol():
    try:
        reg_path = r"Software\\Policies\\Microsoft\\Windows\\System"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
            winreg.SetValueEx(key, "DisableCMD", 0, winreg.REG_DWORD, 0)
        print("[SentinelIT] CMD lockdown lifted. Monitoring only.")
        log_event("lockdown", "CMD lockdown registry policy set to allow")
    except Exception as e:
        print(f"[SentinelIT] Lockdown protocol error: {e}")
        log_event("lockdown", f"Error during lockdown: {e}")

def start():
    print("[Lockdown] Module initiated.")
    lockdown_protocol()
    while True:
        time.sleep(3600)  # Keeps thread alive for long-term monitoring
