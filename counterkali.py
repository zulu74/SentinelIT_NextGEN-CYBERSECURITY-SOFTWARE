"""
SentinelIT Recon/Enumeration Defense Script
Detects and counters tools from Kali Linux, Parrot OS, and Metasploitable.
"""

import socket
import time
import logging

# Setup logging
logging.basicConfig(filename="intrusion_attempts.log", level=logging.INFO, format="%(asctime)s - %(message)s")

# Simulated detection patterns
TOOL_SIGNATURES = {
    "nmap": ["nmap", "Nmap Scripting Engine"],
    "netcat": ["nc", "netcat"],
    "nikto": ["Nikto"],
    "dirb": ["Dirb"],
    "dirbuster": ["DirBuster"],
    "whatweb": ["WhatWeb"],
    "wpscan": ["WPScan"],
    "metasploit": ["Meterpreter", "msf"],
    "parrot": ["parrot", "Parrot OS", "parrotsec"],
    "metasploitable": ["exploit-db", "backdoor", "ms08_067"]
}

FAKE_RESPONSES = {
    "status_code": 200,
    "headers": {
        "Server": "Apache/2.4.1",
        "X-Powered-By": "PHP/5.4.0"
    },
    "body": "<html><body><h1>Nothing here</h1></body></html>"
}

def detect_intruder(user_agent: str, payload: str) -> str:
    """
    Check if user agent or payload contains known attacker signatures.
    """
    for tool, signatures in TOOL_SIGNATURES.items():
        for sig in signatures:
            if sig.lower() in user_agent.lower() or sig.lower() in payload.lower():
                return tool
    return ""

def respond_to_intrusion(tool: str):
    """
    Log and take action based on the tool detected.
    """
    logging.warning(f"Intrusion attempt detected: {tool}")
    if tool in ["nmap", "wpscan", "nikto", "whatweb", "dirb", "dirbuster"]:
        print(f"[!] Recon tool '{tool}' detected. Sending fake response.")
        return FAKE_RESPONSES
    elif tool in ["metasploit", "parrot", "metasploitable"]:
        print(f"[!] Active threat '{tool}' detected. Blocking connection.")
        return {"status": "blocked"}
    else:
        print("[*] No known tool detected.")
        return {"status": "normal"}

# Simulate detection
if __name__ == "__main__":
    test_inputs = [
        ("Mozilla/5.0 (Nikto)", "GET / HTTP/1.1"),
        ("parrot user-agent", "attempt to open shell"),
        ("curl/7.68.0", "Meterpreter payload here"),
        ("ms08_067 exploit", "trigger vulnerable SMB")
    ]

    for ua, payload in test_inputs:
        tool_found = detect_intruder(ua, payload)
        if tool_found:
            respond_to_intrusion(tool_found)
        else:
            print("[+] Normal traffic.")
