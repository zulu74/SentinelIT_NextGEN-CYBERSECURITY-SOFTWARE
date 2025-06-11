
# BeEF.py - Browser Exploitation Framework launcher (template)
# Note: This is a launcher wrapper for BeEF on local systems or VMs.

import os
import subprocess
import platform

def launch_beef():
    print("[*] Launching BeEF (Browser Exploitation Framework)...")

    if platform.system() == "Linux":
        try:
            subprocess.call(["xterm", "-e", "cd /usr/share/beef-xss && ./beef"])
        except Exception as e:
            print("Error launching BeEF:", e)
    else:
        print("BeEF is designed to run on Linux/Kali environments.")

if __name__ == "__main__":
    launch_beef()
