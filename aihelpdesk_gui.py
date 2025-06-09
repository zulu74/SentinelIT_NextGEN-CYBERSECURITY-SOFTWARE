
import tkinter as tk
from tkinter import messagebox
import json
import time
import os

# Placeholder staff data (will expand later for multi-user/company)
staff_data = {
    "fullname": "James Zulu",
    "id_number": "8010115304082",
    "email": "jameszulu1574@gmail.com"
}

# Risky user log path
risky_log_path = "risky_users.json"

# Logging event
def log_event(message):
    with open("sentinel_events.log", "a") as f:
        f.write(f"[AIHelpDeskGUI] {time.ctime()}: {message}\n")

# Risky user logging
def log_risky_user(name, id_number):
    user = {"name": name, "id": id_number, "time": time.ctime()}
    if os.path.exists(risky_log_path):
        with open(risky_log_path, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(user)
    with open(risky_log_path, "w") as f:
        json.dump(data, f, indent=2)

# GUI Verification Logic
def verify_identity():
    name = entry_name.get()
    id_number = entry_id.get()

    if name.strip().lower() == staff_data["fullname"].lower() and id_number.strip() == staff_data["id_number"]:
        log_event(f"SUCCESS: {name} verified.")
        messagebox.showinfo("✅ Verified", "Identity confirmed. Session will be restored.")
        result_label.config(text="✅ Login Session Recovered", fg="green")
    else:
        log_event(f"FAILED attempt: {name} with ID {id_number}")
        log_risky_user(name, id_number)
        messagebox.showerror("❌ Failed", "Verification failed. Admin has been notified.")
        result_label.config(text="❌ Unauthorized attempt logged", fg="red")

# GUI Layout
root = tk.Tk()
root.title("SentinelIT – AI Helpdesk")
root.geometry("400x300")
root.resizable(False, False)

tk.Label(root, text="SentinelIT AI Helpdesk", font=("Arial", 16)).pack(pady=10)
tk.Label(root, text="Full Name").pack()
entry_name = tk.Entry(root, width=40)
entry_name.pack(pady=5)

tk.Label(root, text="ID Number").pack()
entry_id = tk.Entry(root, width=40)
entry_id.pack(pady=5)

tk.Button(root, text="Verify & Restore", command=verify_identity, bg="green", fg="white").pack(pady=15)

result_label = tk.Label(root, text="", font=("Arial", 12))
result_label.pack()

root.mainloop()
