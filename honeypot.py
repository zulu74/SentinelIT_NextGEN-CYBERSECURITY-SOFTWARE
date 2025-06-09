
import os

def deploy_honeypot():
    print("[+] Deploying honeypot...")

    # Create a fake service folder to lure intruders
    fake_path = "C:\\ProgramData\\Windows_Backup_System"
    os.makedirs(fake_path, exist_ok=True)

    # Create fake decoy files
    files = ["AdminPassword.txt", "Finance_Records.xlsx", "AccessKeys.json"]
    for fname in files:
        full_path = os.path.join(fake_path, fname)
        with open(full_path, "w") as f:
            f.write("** Sensitive file: restricted **\n")

    print(f"[+] Honeypot deployed at: {fake_path}")
    return fake_path

# For direct test
if __name__ == "__main__":
    deploy_honeypot()
