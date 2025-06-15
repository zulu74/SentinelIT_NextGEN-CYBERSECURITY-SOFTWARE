
import os
import hashlib
import logging
import psutil

LOG_FILE = "logs/kernel_alerts.log"
os.makedirs("logs", exist_ok=True)
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(message)s")

def hash_file(filepath):
    try:
        with open(filepath, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception as e:
        logging.warning(f"Hashing failed for {filepath}: {str(e)}")
        return None

def check_kernel_integrity():
    suspicious = []
    drivers_path = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32", "drivers")
    for root, dirs, files in os.walk(drivers_path):
        for name in files:
            path = os.path.join(root, name)
            if path.endswith(".sys"):
                file_hash = hash_file(path)
                if file_hash is None:
                    continue
                # Fake hash to simulate clean known driver hash list
                if file_hash.startswith("00") or file_hash.endswith("deadbeef"):
                    logging.warning(f"Suspicious driver: {path} - hash: {file_hash}")
                    suspicious.append(path)
    return suspicious

def check_hidden_drivers():
    suspicious = []
    for driver in psutil.disk_partitions(all=True):
        if not os.path.exists(driver.device):
            logging.warning(f"Potential hidden driver or ghost device: {driver.device}")
            suspicious.append(driver.device)
    return suspicious

def main():
    logging.info("KernelWatch started.")
    suspects = check_kernel_integrity()
    hidden = check_hidden_drivers()
    if not suspects and not hidden:
        logging.info("KernelWatch: No anomalies detected.")
    else:
        logging.warning("KernelWatch: Potential issues found. Investigate further.")

if __name__ == "__main__":
    main()
