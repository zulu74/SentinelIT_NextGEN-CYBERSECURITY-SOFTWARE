#!/usr/bin/env python3
"""
packetshield.py — Network Packet Protection for SentinelIT

Features:
- Monitors network interfaces for suspicious traffic
- Emits events to CloudWatch for logging and S3 sync
- Threaded background monitoring
"""

import threading
import time
import psutil
import random  # simulate packet events for now

from cloudwatch import emit_event

INTERFACES = ["eth0", "wlan0"]  # adjust to actual interfaces
SCAN_INTERVAL = 5  # seconds

# Example detection heuristics (simulated)
SUSPICIOUS_DST = ["192.168.1.100", "10.0.0.200"]

def monitor_interface(interface: str):
    emit_event("PacketShield", "module_start", {"module": "PacketShield", "interface": interface})
    print(f"[PacketShield] Monitoring interface {interface}")

    while True:
        # Simulate packet monitoring
        pkt_src = f"10.0.0.{random.randint(2,254)}"
        pkt_dst = random.choice(["192.168.1.10", "192.168.1.100", "10.0.0.50", "10.0.0.200"])
        alert_type = None

        if pkt_dst in SUSPICIOUS_DST:
            alert_type = "suspicious_destination"
            emit_event("PacketShield", "packet_alert", {
                "interface": interface,
                "src": pkt_src,
                "dst": pkt_dst,
                "alert": alert_type
            })
            print(f"[PacketShield] ALERT | {pkt_src} -> {pkt_dst} | {alert_type}")

        time.sleep(SCAN_INTERVAL)

def start():
    threads = []
    for iface in INTERFACES:
        t = threading.Thread(target=monitor_interface, args=(iface,), daemon=True)
        t.start()
        threads.append(t)

def main():
    start()
    while True:
        time.sleep(60)  # keep main thread alive for daemon threads

if __name__ == "__main__":
    main()

