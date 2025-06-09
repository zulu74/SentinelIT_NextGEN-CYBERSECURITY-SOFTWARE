
import logging
import os

log_file = "C:/opt/SentinelIT/logs/authlock.log"
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(message)s")

AUTHORIZED = ["Costaz36#__$$", "Myworks--X51", "Nextgen**74"]  # Example placeholders
DURESS = ["HELP", "FORCE", "FAKE"]

def run():
    print("[AUTHLOCK] Enter 3 executive OTPs to unlock system:")
    user_otps = []
    for i in range(1, 4):
        otp = input(f"Enter OTP {i}: ").strip().upper()
        user_otps.append(otp)
    if any(code in DURESS for code in user_otps):
        logging.critical("[AUTHLOCK] Duress code entered! Silent alert triggered.")
        print("[AUTHLOCK] ALERT: Duress detected!")
        return
    elif all(code in AUTHORIZED for code in user_otps):
        print("[AUTHLOCK] Access granted. CMD and PowerShell temporarily enabled.")
        logging.info("Triple OTP validated. Shell access temporarily allowed.")
    else:
        print("[AUTHLOCK] Invalid OTPs. CMD/PowerShell lockdown in place.")
        logging.warning("Invalid OTP attempt. Lockdown maintained.")
