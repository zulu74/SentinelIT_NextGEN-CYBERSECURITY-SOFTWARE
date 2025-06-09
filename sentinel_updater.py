import os
import subprocess

def update_sentinelIT():
    print("[Updater] Checking for latest updates from GitHub...")

    try:
        # Change to your SentinelIT directory
        os.chdir(r"C:\Users\xzola\Downloads\SentinelIT_Build")

        # Pull from GitHub
        subprocess.run(["git", "pull"], check=True)

        print("[Updater] All SentinelIT files have been updated.")
    except Exception as e:
        print("[Updater] Update failed:", e)

if __name__ == "__main__":
    update_sentinelIT()
