# netviz.py – Phase 7: Network Visualization

import json
import os

def run_netviz():
    print("[NETVIZ] Visualizing OT/ICS network topology...")

    network_map = {
        "PLC-1": ["HMI-1", "Historian"],
        "HMI-1": ["PLC-1", "Engineering Workstation"],
        "Historian": ["PLC-1", "Corporate DB"],
        "Firewall": ["Engineering Workstation", "Corporate DB"]
    }

    os.makedirs("logs", exist_ok=True)
    with open("logs/network_map.json", "w") as f:
        json.dump(network_map, f, indent=4)

    print("[NETVIZ] Network topology map exported to logs/network_map.json") 