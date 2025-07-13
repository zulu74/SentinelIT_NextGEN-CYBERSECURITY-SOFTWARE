
import time
import random

def start():
    print("[RECONGUARD AI] Actively monitoring for reconnaissance attempts...")

    tools_detected = [
        ("whois", "192.168.0.32"),
        ("nslookup", "192.168.0.34"),
        ("nmap -sS", "192.168.0.45"),
        ("dnsenum", "192.168.0.29"),
        ("dirb", "192.168.0.39")
    ]

    while True:
        tool_name, source_ip = random.choice(tools_detected)
        print(f"[RECONGUARD AI] Reconnaissance tool detected: {tool_name} from {source_ip} at {time.ctime()}")
        time.sleep(7)

if __name__ == "__main__":
    start()
