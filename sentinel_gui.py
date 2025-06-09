try:
    from PIL import Image, ImageTk
except ImportError:
    import os
    os.system('pip install Pillow')
    from PIL import Image, ImageTk

import os
import tkinter as tk
from tkinter import messagebox

# Function to run SentinelIT
def run_sentinel():
    os.system("python main.py")
    messagebox.showinfo("Run Complete", "SentinelIT execution completed.")

# Function to view logs
def view_logs():
    log_dir = os.path.join(os.getcwd(), "logs")
    if os.path.exists(log_dir):
        os.startfile(log_dir)
    else:
        messagebox.showerror("Error", "Log directory not found.")

# Function to generate report
def generate_report():
    os.system("python reportgen.py")
    messagebox.showinfo("Report", "PDF Report generated successfully.")

# Function to view threat summary
def view_threats():
    path = os.path.join(os.getcwd(), "SentinelIT_Risk_Report.pdf")
    if os.path.exists(path):
        os.startfile(path)
    else:
        messagebox.showerror("Error", "Report not found. Run the report generator first.")

# Create main window
root = tk.Tk()
root.title("SentinelIT GUI Dashboard")
root.geometry("600x400")
root.configure(bg="white")

# Watermark image
try:
    shield_img = Image.open("shield_watermark.png").resize((400, 400))
    shield_img.putalpha(70)
    shield_tk = ImageTk.PhotoImage(shield_img)
    bg_label = tk.Label(root, image=shield_tk, bg="white")
    bg_label.place(x=100, y=0)
except:
    pass

# Title
title = tk.Label(root, text="SentinelIT GUI Dashboard", font=("Arial", 16, "bold"), bg="white", fg="#003366")
title.pack(pady=10)

# Buttons
btn1 = tk.Button(root, text="▶ Run SentinelIT", font=("Arial", 12), width=25, command=run_sentinel)
btn2 = tk.Button(root, text="📖 View Logs", font=("Arial", 12), width=25, command=view_logs)
btn3 = tk.Button(root, text="📄 Generate PDF Report", font=("Arial", 12), width=25, command=generate_report)
btn4 = tk.Button(root, text="📊 View Threat Summary", font=("Arial", 12), width=25, command=view_threats)
btn5 = tk.Button(root, text="❌ Exit Dashboard", font=("Arial", 12), width=25, command=root.quit)

# Place buttons
for btn in (btn1, btn2, btn3, btn4, btn5):
    btn.pack(pady=5)

# Start loop
root.mainloop()
