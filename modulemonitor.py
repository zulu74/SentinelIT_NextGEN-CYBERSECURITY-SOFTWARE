
import tkinter as tk
from tkinter import ttk, messagebox

class ModuleMonitor(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Module Monitor")
        self.geometry("500x400")
        self.configure(bg="#1c1c1c")

        title = tk.Label(self, text="SentinelIT Module Monitor", font=("Segoe UI", 16), fg="white", bg="#1c1c1c")
        title.pack(pady=10)

        self.module_list = tk.Listbox(self, bg="#2e2e2e", fg="lightgreen", font=("Segoe UI", 12), height=12, selectbackground="red")
        self.module_list.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        refresh_btn = ttk.Button(self, text="Refresh Modules", command=self.refresh_modules)
        refresh_btn.pack(pady=10)

        self.refresh_modules()

    def refresh_modules(self):
        self.module_list.delete(0, tk.END)
        # Simulated list of running modules (in real scenario, parse actual process/module logs)
        modules = ["lockdown.py", "ai_core.py", "dashboard_server.py", "cloudwatch.py", "siemcore_ai.py"]
        for mod in modules:
            self.module_list.insert(tk.END, f" {mod} (Running)")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    ModuleMonitor(root).mainloop()
