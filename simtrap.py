import logging
import time

log_file = "C:/opt/SentinelIT/logs/simtrap.log"
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(message)s")

def monitor_decoys():
    print("[SIMTRAP] Monitoring honeypot decoy environment...")
    logging.info("Monitoring honeypot environment for interaction...")

    # Simulate detection logic
    time.sleep(2)
    print("[SIMTRAP] Unauthorized access detected on honeypot!")
    logging.warning("Unauthorized access detected on decoy file.")
