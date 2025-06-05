
import getpass

def run():
    print("[AUTHLOCK] Enter 3 executive OTPs to unlock system:")
    expected_otps = [
        "Costaz36#__$$",
        "Myworks--X51",
        "Nextgen**74"
    ]
    for i, otp_label in enumerate(["OTP 1", "OTP 2", "OTP 3"]):
        code = getpass.getpass(f"Enter {otp_label}: ")
        if code != expected_otps[i]:
            print("[AUTHLOCK] Invalid OTPs. CMD/PowerShell lockdown in place.")
            return False
    print("[AUTHLOCK] All executive approvals received. System unlocked.")
    return True
