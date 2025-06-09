
import os
import ctypes
import winreg

def enable_cmd_and_powershell():
    print("[+] Attempting to restore CMD and PowerShell access...")

    try:
        # Re-enable CMD via registry
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Software\Policies\Microsoft\Windows\System",
                            0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "DisableCMD", 0, winreg.REG_DWORD, 0)
            print("[✓] CMD access restored via registry.")
    except FileNotFoundError:
        print("[i] Registry key not found, nothing to undo for CMD.")
    except PermissionError:
        print("[!] Insufficient permissions to edit registry. Run as admin.")

    try:
        # Re-enable PowerShell by renaming the backup or restoring execution policy
        os.system("powershell -Command "Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force"")
        print("[✓] PowerShell execution policy restored.")
    except Exception as e:
        print(f"[!] Error restoring PowerShell: {e}")

    print("[✓] Recovery script completed. Try opening CMD or PowerShell again.")

if __name__ == "__main__":
    # Ensure running with admin rights
    if ctypes.windll.shell32.IsUserAnAdmin():
        enable_cmd_and_powershell()
    else:
        print("[!] Please run this script as Administrator.")
