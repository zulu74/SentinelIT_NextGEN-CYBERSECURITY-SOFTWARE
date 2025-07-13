
<<<<<<< HEAD
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
=======
def helpdesk_bot():
    print("[+] SentinelIT Helpdesk Assistant is now active.")
    print("    - Type 'reset password' to simulate password assistance.")
    print("    - Type 'login issue' to simulate login support.")
    print("    - Type 'exit' to quit.\n")

    while True:
        user_input = input("Helpdesk >> ").strip().lower()

        if user_input == "reset password":
            print("[+] Simulating password reset... New password sent to user's recovery email.")
        elif user_input == "login issue":
            print("[+] Checking login logs... No suspicious activity. Suggest user tries again.")
        elif user_input == "exit":
            print("[✓] Exiting helpdesk assistant.")
            break
        else:
            print("[!] Unrecognized request. Try: 'reset password', 'login issue', or 'exit'.")

# For direct test
if __name__ == "__main__":
    helpdesk_bot()
>>>>>>> temp-patch
