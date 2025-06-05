
import time
import re
import os
import pyperclip

def scan_clipboard():
    clipboard = pyperclip.paste()
    phishing_patterns = [
        r"http[s]?://[^ ]*\.zip",
        r"http[s]?://[^ ]*\.exe",
        r"http[s]?://[^ ]*\.scr",
        r"http[s]?://[^ ]*\.php",
        r"http[s]?://[^ ]*login[^ ]*",
        r"http[s]?://[^ ]*account[^ ]*"
    ]
    for pattern in phishing_patterns:
        if re.search(pattern, clipboard, re.IGNORECASE):
            print(f"[ALERT] Suspicious clipboard URL: {clipboard}")
            log_detection(clipboard)

def log_detection(data):
    folder = "logs"
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, "phishing_links.txt"), "a") as file:
        file.write(f"{time.ctime()} - {data}\n")

def run_mailwatch():
    print("[MailWatch] Monitoring clipboard and email link patterns...")
    while True:
        scan_clipboard()
        time.sleep(5)
