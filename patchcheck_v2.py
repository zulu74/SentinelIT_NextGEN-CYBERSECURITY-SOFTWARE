
import platform
import subprocess
import os

def check_patches():
    system = platform.system()

    print(f"[+] Checking patches for: {system}")

    if system == "Windows":
        try:
            result = subprocess.check_output("wmic qfe list full", shell=True)
            print("[+] Installed Windows patches:")
            print(result.decode(errors="ignore"))
        except Exception as e:
            print(f"[!] Error checking patches on Windows: {e}")

    elif system == "Linux":
        try:
            if os.path.exists("/usr/bin/apt"):
                result = subprocess.check_output("apt list --installed", shell=True)
            elif os.path.exists("/usr/bin/yum"):
                result = subprocess.check_output("yum list installed", shell=True)
            else:
                print("[!] Unsupported Linux package manager.")
                return

            print("[+] Installed Linux packages:")
            print(result.decode(errors="ignore"))
        except Exception as e:
            print(f"[!] Error checking patches on Linux: {e}")

    else:
        print("[!] Unsupported Operating System")

# Allow running as standalone for testing
if __name__ == "__main__":
    check_patches()
