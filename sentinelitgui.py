# sentinelitgui.py — SentinelIT Console (Full Version)

import tkinter as tk
from tkinter import ttk
import threading
from sentinelIT import sentinel_hub

#  SentinelIT Dark Color Theme
BG_COLOR = "#0D1117"
ACCENT_COLOR = "#00FF88"
TEXT_COLOR = "#FFFFFF"
BTN_COLOR = "#3399FF"
GREEN = "#22FF22"
RED = "#FF4444"

#  Module names (must match thread names in sentinel_hub MODULE_REGISTRY)
MONITORED_MODULES = [
    "USBWatch",
    "NetWatch",
    "PhantomStaff",
    "ThreatDNA",
    "ComplianceMonitor"
]

def get_thread_status_map():
    """Map each module name to whether its thread is running."""
    active_threads = threading.enumerate()
    thread_names = [t.name for t in active_threads]
    return {mod: (mod in thread_names) for mod in MONITORED_MODULES}

def update_status_labels():
    """Refresh the label color/text based on thread activity."""
    thread_map = get_thread_status_map()
    for mod, label in status_labels.items():
        is_running = thread_map.get(mod, False)
        label.configure(
            text="Running" if is_running else "Stopped",
            fg=GREEN if is_running else RED
        )
    # Recheck in 2 seconds
    status_labels["USBWatch"].after(2000, update_status_labels)

def start_all_modules():
    """Trigger all modules from sentinel_hub."""
    sentinel_hub.start_all()

def main():
    global status_labels
    status_labels = {}

    root = tk.Tk()
    root.title("SentinelIT: Security Command Console")
    root.geometry("800x500")
    root.configure(bg=BG_COLOR)

    #  Style
    style = ttk.Style()
    style.theme_use("default")
    style.configure("Accent.TButton", background=BTN_COLOR, foreground="white")

    #  Title Header
    title = tk.Label(root, text="SentinelIT: Security Command Console",
                     font=("Segoe UI", 20, "bold"), fg=ACCENT_COLOR, bg=BG_COLOR)
    title.pack(pady=20)

    #  Module Status Panel
    main_frame = tk.Frame(root, bg=BG_COLOR)
    main_frame.pack(fill="both", expand=True)

    for mod in MONITORED_MODULES:
        row = tk.Frame(main_frame, bg=BG_COLOR)
        row.pack(anchor="w", pady=6, padx=40)

        name_label = tk.Label(row, text=mod, font=("Segoe UI", 12), fg=TEXT_COLOR, bg=BG_COLOR)
        name_label.pack(side="left", padx=(0, 20))

        status = tk.Label(row, text="Pending", font=("Segoe UI", 12, "bold"), fg=TEXT_COLOR, bg=BG_COLOR)
        status.pack(side="left")

        status_labels[mod] = status

    #  Launch Controls
    btn_frame = tk.Frame(root, bg=BG_COLOR)
    btn_frame.pack(pady=30)

    start_btn = ttk.Button(btn_frame, text="Start All Modules",
                           style="Accent.TButton", command=start_all_modules)
    start_btn.pack()

    #  Dev Footer
    footer = tk.Label(root, text="SentinelIT v1.0 — Powered by Modular Intelligence",
                      font=("Segoe UI", 9), fg="#777777", bg=BG_COLOR)
    footer.pack(side="bottom", pady=10)

    #  Begin Refresh Loop
    update_status_labels()

    root.mainloop()

if __name__ == "__main__":
    main()