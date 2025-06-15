import hashlib
import os
import time
import json
import socket
from datetime import datetime
from cryptography.fernet import Fernet

# Configuration
HEARTBEAT_INTERVAL = 300  # 5 minutes
STATUS_FILE = "logs/heartbeat_status.json"
KEY_FILE = "heartbeat_key.key"

# Generate encryption key if not exists
def generate_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, 'wb') as key_file:
            key_file.write(key)

# Load encryption key
def load_key():
    with open(KEY_FILE, 'rb') as key_file:
        return key_file.read()

# Encrypt and save heartbeat status
def save_heartbeat_status(status):
    key = load_key()
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(json.dumps(status).encode())
    with open(STATUS_FILE, 'wb') as status_file:
        status_file.write(encrypted_data)

# Main heartbeat function
def send_heartbeat():
    while True:
        status = {
            "timestamp": datetime.utcnow().isoformat(),
            "hostname": socket.gethostname(),
            "status": "ACTIVE",
            "modules": os.listdir("modules") if os.path.exists("modules") else [],
        }
        save_heartbeat_status(status)
        time.sleep(HEARTBEAT_INTERVAL)

if __name__ == "__main__":
    generate_key()
    send_heartbeat()
