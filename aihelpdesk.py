
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
