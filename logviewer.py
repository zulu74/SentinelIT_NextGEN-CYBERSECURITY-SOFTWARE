
import tkinter as tk
from tkinter import scrolledtext
import os

class LogViewer:
    def __init__(self, master):
        self.master = master
        self.master.title("SentinelIT – Log Viewer")
        self.master.geometry("700x500")
        self.text_area = scrolledtext.ScrolledText(master, wrap=tk.WORD, font=("Consolas", 10))
        self.text_area.pack(fill=tk.BOTH, expand=True)
        self.load_logs()

    def load_logs(self):
        logs_dir = "logs"
        combined_logs = ""
        if os.path.isdir(logs_dir):
            for file_name in os.listdir(logs_dir):
                file_path = os.path.join(logs_dir, file_name)
                if file_path.endswith(".log"):
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
                            combined_logs += f"--- {file_name} ---\n"
                            combined_logs += file.read() + "\n\n"
                    except Exception as e:
                        combined_logs += f"[Error reading {file_name}]: {e}\n"
        else:
            combined_logs = "No logs directory found."

        self.text_area.insert(tk.END, combined_logs)
        self.text_area.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = LogViewer(root)
    root.mainloop()
