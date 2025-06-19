import time
import random

def start():
    print("[KALITRAP] Actively blocking reconnaissance tools from Kali Linux...")

    tools_blocked = [
        ("nmap", "192.168.0.102"),
        ("wireshark", "192.168.0.88"),
        ("hydra", "192.168.0.51"),
        ("john", "192.168.0.47"),
        ("metasploit", "192.168.0.99")
    ]

    while True:
        tool_name, source_ip = random.choice(tools_blocked)
        print(f"[KALITRAP] Blocked Tool: {tool_name} from {source_ip} at {time.ctime()}")
        time.sleep(9)

if __name__ == "__main__":
    start()

