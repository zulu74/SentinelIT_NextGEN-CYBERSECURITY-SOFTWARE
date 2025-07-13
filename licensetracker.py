
import os
import json
import datetime
from tkinter import messagebox

LICENSE_FILE = "sentinel_license.json"

def create_trial_license():
    if not os.path.exists(LICENSE_FILE):
        trial_info = {
            "status": "trial",
            "start_date": str(datetime.date.today()),
            "duration_days": 30,
            "activated": False,
            "license_key": ""
        }
        with open(LICENSE_FILE, "w") as f:
            json.dump(trial_info, f)

def load_license():
    if not os.path.exists(LICENSE_FILE):
        create_trial_license()
    with open(LICENSE_FILE, "r") as f:
        return json.load(f)

def save_license(data):
    with open(LICENSE_FILE, "w") as f:
        json.dump(data, f)

def days_left(trial_info):
    start_date = datetime.datetime.strptime(trial_info["start_date"], "%Y-%m-%d").date()
    today = datetime.date.today()
    used_days = (today - start_date).days
    return max(0, trial_info["duration_days"] - used_days)

def is_trial_expired():
    license_data = load_license()
    return days_left(license_data) <= 0 and not license_data["activated"]

def activate_license(input_key):
    # Simple static key (can be replaced with hashed server check)
    VALID_KEYS = ["SENTINELPRO-2025-KEY"]
    license_data = load_license()
    if input_key in VALID_KEYS:
        license_data["activated"] = True
        license_data["status"] = "pro"
        license_data["license_key"] = input_key
        save_license(license_data)
        return True
    return False

def show_license_status():
    data = load_license()
    if data["activated"]:
        status = f"License: PRO\nActivated Key: {data['license_key']}"
    else:
        status = f"License: TRIAL\nDays left: {days_left(data)}"
    messagebox.showinfo("License Info", status)
