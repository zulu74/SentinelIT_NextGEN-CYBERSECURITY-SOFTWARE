import logging
import os

log_file = "C:/opt/SentinelIT/logs/decoygen.log"
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(message)s")

def generate_decoy_logs():
    log_path = os.path.join(os.getcwd(), "decoys", "decoy_activity.log")
    with open(log_path, "w") as f:
        f.write("[LOG] Honeypot accessed: AdminPasswords.txt\n")
        f.write("[LOG] Possible exfiltration attempt on Payroll_2025.xlsx\n")
    logging.info("Generated decoy activity logs")
    print("[DECOYGEN] Decoy activity logs generated.")
