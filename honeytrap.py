
import socket
import threading
import logging

def run_honeytrap():
    logging.basicConfig(filename='honeytrap.log', level=logging.INFO, format='%(asctime)s - %(message)s')
    fake_services = [21, 22, 23, 80, 443, 8080]  # Common ports to simulate
    threads = []

    def trap(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('0.0.0.0', port))
            s.listen(1)
            logging.info(f"Honeypot listening on port {port}")
            while True:
                conn, addr = s.accept()
                logging.info(f"Connection attempt from {addr[0]} on port {port}")
                conn.close()

    for port in fake_services:
        t = threading.Thread(target=trap, args=(port,), daemon=True)
        threads.append(t)
        t.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        logging.info("Honeypot shutting down.")
