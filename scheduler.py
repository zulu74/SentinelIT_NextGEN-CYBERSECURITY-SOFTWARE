
import schedule
import time
import subprocess

def run_weekly_reports():
    try:
        subprocess.run(["python", "reportmanager.py"], check=True)
        print("Weekly report generated successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error generating report: {e}")

# Schedule the report generation every Sunday at 7 AM
schedule.every().sunday.at("07:00").do(run_weekly_reports)

print("SentinelIT Scheduler is running...")

while True:
    schedule.run_pending()
    time.sleep(60)
