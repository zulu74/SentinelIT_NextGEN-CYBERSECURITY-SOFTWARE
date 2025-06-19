import time
import random

def start():
    print("[PhantomStaff] AI Helpdesk & Staff Monitoring initialized...")

    staff_events = [
        "Password reset requested by staff ID 001",
        "Unauthorized login detected for staff ID 105",
        "Helpdesk query: VPN not connecting",
        "Security alert: Silent duress trigger from reception",
        "Access attempt blocked: Invalid staff clearance level"
    ]

    while True:
        event = random.choice(staff_events)
        print(f"[PhantomStaff] {event}")
        time.sleep(7)
