import tkinter as tk
from tkinter import messagebox
import datetime
import os

# License file path
LICENSE_FILE = "sentinel_license.key"
TRIAL_PERIOD_DAYS = 30

class ActivationWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("SentinelIT Activation")
        self.root.geometry("400x250")

        tk.Label(root, text="SentinelIT - Activation", font=("Helvetica", 16, "bold")).pack(pady=10)

        self.entry = tk.Entry(root, width=35)
        self.entry.pack(pady=10)
        self.entry.insert(0, "Enter License Key")

        self.activate_btn = tk.Button(root, text="Activate", command=self.activate)
        self.activate_btn.pack(pady=10)

        self.status_label = tk.Label(root, text="", fg="red")
        self.status_label.pack(pady=5)

        # Check license on load
        self.check_license()

    def activate(self):
        key = self.entry.get().strip()
        if key == "SENTINELIT-2024-ACTIVE-KEY":
            with open(LICENSE_FILE, "w") as f:
                f.write("ACTIVATED")
            messagebox.showinfo("Success", "SentinelIT Activated!")
            self.status_label.config(text="Activated", fg="green")
        else:
            messagebox.showerror("Error", "Invalid License Key")

    def check_license(self):
        if os.path.exists(LICENSE_FILE):
            with open(LICENSE_FILE, "r") as f:
                content = f.read().strip()
                if content == "ACTIVATED":
                    self.status_label.config(text="Activated", fg="green")
                    return
        else:
            # Trial Logic
            trial_file = "trial_start.date"
            if not os.path.exists(trial_file):
                with open(trial_file, "w") as f:
                    f.write(str(datetime.date.today()))

            with open(trial_file, "r") as f:
                start_date = datetime.datetime.strptime(f.read().strip(), "%Y-%m-%d").date()

            days_used = (datetime.date.today() - start_date).days
            days_left = TRIAL_PERIOD_DAYS - days_used

            if days_left <= 0:
                self.status_label.config(text="Trial Expired. Enter License Key.", fg="red")
                self.activate_btn.config(state=tk.NORMAL)
            else:
                self.status_label.config(text=f"Trial Mode: {days_left} days left", fg="orange")
                self.activate_btn.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = ActivationWindow(root)
    root.mainloop()
