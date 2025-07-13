# integrate_activation.py

import os
import subprocess

# Check if SentinelIT is activated
activation_file = "activation_status.txt"

if os.path.exists(activation_file):
    with open(activation_file, "r") as f:
        status = f.read().strip()
    if status == "activated":
        print("SentinelIT Activated. Launching system...")
        subprocess.run(["python", "ultimate_main.py"])
    else:
        print("Trial Expired or Not Activated.")
        subprocess.run(["python", "activation_gui.py"])
else:
    # First time run, trigger activation GUI
    subprocess.run(["python", "activation_gui.py"])
    
    # After GUI closes, check again
    if os.path.exists(activation_file):
        with open(activation_file, "r") as f:
            status = f.read().strip()
        if status == "activated":
            subprocess.run(["python", "ultimate_main.py"])
        else:
            print("Activation required. Exiting.")
