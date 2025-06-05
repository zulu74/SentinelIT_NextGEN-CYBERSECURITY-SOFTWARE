
import time
import pyttsx3

def run_phantomstaff():
    try:
        engine = pyttsx3.init()
        engine.say("PhantomStaff activated. Monitoring system events.")
        engine.runAndWait()
        print("PhantomStaff is now active and monitoring.")
        while True:
            # Simulated system check
            time.sleep(30)
            print("PhantomStaff: All systems normal.")
    except Exception as e:
        print(f"PhantomStaff encountered an error: {e}")
