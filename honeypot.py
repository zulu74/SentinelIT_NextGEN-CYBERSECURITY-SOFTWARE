
import time
import logging

def run_honeypot():
    logging.basicConfig(filename='logs/honeypot.log', level=logging.INFO, format='%(asctime)s %(message)s')
    print("[HONEYPOT] Honeypot module started. Monitoring for unauthorized access attempts...")

    try:
        while True:
            # Simulated honeypot activity
            fake_services = ["FTP", "RDP", "Telnet", "SMB"]
            for service in fake_services:
                logging.info(f"Honeypot active on {service} port.")
                print(f"[HONEYPOT] Fake {service} service active (trap).")
                time.sleep(1)
            time.sleep(5)
    except KeyboardInterrupt:
        print("[HONEYPOT] Honeypot monitoring stopped.")
