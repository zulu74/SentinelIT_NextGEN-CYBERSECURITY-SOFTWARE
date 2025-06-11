
# packetshield.py - Passive Packet Monitoring for SentinelIT (Phase 8)
import scapy.all as scapy
import logging
from datetime import datetime

log_file = "packetshield_log.txt"
logging.basicConfig(filename=log_file, level=logging.INFO)

MALICIOUS_SIGNATURES = [
    "nmap", "nikto", "sqlmap", "malware", "powershell", "curl", "wget", "payload", "exploit"
]

def detect_payload(packet):
    try:
        if packet.haslayer(scapy.Raw):
            payload = packet[scapy.Raw].load.decode(errors='ignore').lower()
            for signature in MALICIOUS_SIGNATURES:
                if signature in payload:
                    logging.warning(f"[{datetime.now()}] Suspicious traffic detected: {signature.upper()} in payload")
                    print(f"[!] Alert: Suspicious traffic: {signature.upper()} detected")
                    break
    except Exception as e:
        pass  # ignore decode errors

def main():
    print("[PacketShield] Passive packet monitoring started...")
    scapy.sniff(filter="ip", prn=detect_payload, store=0)

if __name__ == "__main__":
    main()
