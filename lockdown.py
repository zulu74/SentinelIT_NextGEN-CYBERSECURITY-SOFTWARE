
import os
import subprocess
import ctypes

ADMIN_PASSWORD = "63978zulu"

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def lock_powershell_and_cmd():
    try:
        print("[*] Locking CMD and PowerShell...")
        cmd_path = r"C:\Windows\System32\cmd.exe"
        ps_path = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"

        for path in [cmd_path, ps_path]:
            subprocess.call(["icacls", path, "/deny", "Everyone:(X)"], shell=True)
        print("[+] CMD and PowerShell access blocked.")
    except Exception as e:
        print(f"[!] Failed to lock CMD/PowerShell: {e}")

def unlock_powershell_and_cmd():
    try:
        password = input("Enter admin password to unlock: ")
        if password == ADMIN_PASSWORD:
            print("[*] Unlocking CMD and PowerShell...")
            cmd_path = r"C:\Windows\System32\cmd.exe"
            ps_path = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"

            for path in [cmd_path, ps_path]:
                subprocess.call(["icacls", path, "/remove:d", "Everyone"], shell=True)
            print("[+] Access restored.")
        else:
            print("[!] Incorrect password.")
    except Exception as e:
        print(f"[!] Failed to unlock CMD/PowerShell: {e}")

if __name__ == "__main__":
    if is_admin():
        action = input("Type 'lock' to lock CMD/PowerShell or 'unlock' to unlock: ").strip().lower()
        if action == "lock":
            lock_powershell_and_cmd()
        elif action == "unlock":
            unlock_powershell_and_cmd()
        else:
            print("Invalid option.")
    else:
        print("Please run this script as Administrator.")
