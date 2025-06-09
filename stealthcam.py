import logging
import datetime

log_file = "C:/opt/SentinelIT/logs/stealthcam.log"
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(message)s")

def stealth_camera():
    now = datetime.datetime.now()
    # Simulated camera capture
    logging.warning(f"[STEALTHCAM] Unauthorized login attempt captured at {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print("[STEALTHCAM] Simulated camera snap on suspicious login.")
