
import tkinter as tk
from tkinter import messagebox

def log_request(full_name, id_number, issue):
    with open("staff_requests.log", "a") as f:
        f.write(f"Name: {full_name}\nID: {id_number}\nIssue: {issue}\n{'-'*40}\n")

def verify():
    full_name = name_entry.get().strip()
    id_number = id_entry.get().strip()
    issue_text = issue_box.get("1.0", "end").strip()

    if not full_name or not id_number or not issue_text:
        messagebox.showerror("Error", "All fields are required.")
        return

    log_request(full_name, id_number, issue_text)
    messagebox.showinfo("Request Logged", "Your issue has been submitted.")
    root.destroy()

# GUI setup
root = tk.Tk()
root.title("SentinelIT – AI Helpdesk")

tk.Label(root, text="Full Name").grid(row=0, column=0, sticky="w", padx=10, pady=5)
name_entry = tk.Entry(root, width=40)
name_entry.grid(row=0, column=1, padx=10)

tk.Label(root, text="ID Number").grid(row=1, column=0, sticky="w", padx=10, pady=5)
id_entry = tk.Entry(root, width=40)
id_entry.grid(row=1, column=1, padx=10)

tk.Label(root, text="Issue Description").grid(row=2, column=0, sticky="nw", padx=10, pady=5)
issue_box = tk.Text(root, width=40, height=8)
issue_box.grid(row=2, column=1, padx=10, pady=5)

tk.Button(root, text="Submit Request", command=verify, bg="green", fg="white").grid(row=3, column=1, sticky="e", padx=10, pady=10)

root.mainloop()
