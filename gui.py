import tkinter as tk
from tkinter import messagebox
import subprocess
import os

class SentinelGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SentinelIT Control Panel")
        self.geometry("420x320")
        self.config(bg="#1e1e1e")

        tk.Label(self, text="SentinelIT GUI Dashboard", fg="white", bg="#1e1e1e", font=("Arial", 16)).pack(pady=20)

        tk.Button(self, text="▶ Run SentinelIT", width=30, command=self.run_sentinel, bg="#2d89ef", fg="white").pack(pady=8)
        tk.Button(self, text="📂 View Main Logs", width=30, command=self.view_logs, bg="#0078d4", fg="white").pack(pady=8)
        tk.Button(self, text="🛡 View Threats", width=30, command=self.view_threats, bg="#107c10", fg="white").pack(pady=8)
        tk.Button(self, text="❌ Exit Dashboard", width=30, command=self.quit, bg="#e81123", fg="white").pack(pady=16)

    def run_sentinel(self):
        try:
            subprocess.run(["python", "main.py"], check=True)
        except subprocess.CalledProcessError:
            messagebox.showerror("Execution Failed", "SentinelIT failed to start.")

    def view_logs(self):
        self._open_log_file("logs/sentinel.log", "System Logs")

    def view_threats(self):
        self._open_log_file("logs/threats.log", "Threat Activity")

    def _open_log_file(self, path, title):
        if not os.path.exists(path):
            messagebox.showwarning("Missing Log", f"{path} not found.")
            return

        with open(path, "r") as f:
            content = f.read()

        top = tk.Toplevel(self)
        top.title(title)
        text = tk.Text(top, wrap=tk.WORD, bg="#f4f4f4")
        text.insert(tk.END, content)
        text.pack(expand=True, fill="both")

if __name__ == "__main__":
    app = SentinelGUI()
    app.mainloop()

