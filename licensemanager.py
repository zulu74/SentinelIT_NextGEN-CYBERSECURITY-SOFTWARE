​You​
import os
import json
import datetime
from cryptography.fernet import Fernet

# Paths
LICENSE_FILE = "license.key"
KEY_FILE = "fernet.key"
TRIAL_DAYS = 30

# Generate a new Fernet key and save
if not os.path.exists(KEY_FILE):
    with open(KEY_FILE, 'wb') as f:
        f.write(Fernet.generate_key())

with open(KEY_FILE, 'rb') as f:
    fernet = Fernet(f.read())

def activate_license(user_name, license_code):
    if license_code and len(license_code) > 10:
        data = {
            "user": user_name,
            "activated_on": str(datetime.date.today()),
            "valid_until": str(datetime.date.today() + datetime.timedelta(days=365)),
            "license_code": license_code
        }
        encrypted = fernet.encrypt(json.dumps(data).encode())
        with open(LICENSE_FILE, 'wb') as f:
            f.write(encrypted)
        return True
    return False

def check_license():
    if not os.path.exists(LICENSE_FILE):
        return False, "Trial Mode"
    try:
        with open(LICENSE_FILE, 'rb') as f:
            decrypted = fernet.decrypt(f.read()).decode()
            data = json.loads(decrypted)
            valid_until = datetime.datetime.strptime(data["valid_until"], "%Y-%m-%d").date()
            if datetime.date.today() <= valid_until:
                return True, data["user"]
            else:
                return False, "License Expired"
    except Exception:
        return False, "Invalid License"

def start_trial():
    if not os.path.exists(LICENSE_FILE):
        trial_start = datetime.date.today()
        trial_end = trial_start + datetime.timedelta(days=TRIAL_DAYS)
        data = {
            "user": "Trial User",
            "activated_on": str(trial_start),
            "valid_until": str(trial_end),
            "license_code": "TRIAL"
        }
        encrypted = fernet.encrypt(json.dumps(data).encode())
        with open(LICENSE_FILE, 'wb') as f:
            f.write(encrypted)
        return True
    return False
