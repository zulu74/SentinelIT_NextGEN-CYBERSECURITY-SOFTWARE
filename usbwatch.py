
import os
import time
import smtplib
import logging
from email.message import EmailMessage
import win32file
import win32api
import cv2

# === CONFIG ===
ADMIN_EMAIL = "james.zulu35@yahoo.co.uk"
SMTP_SERVER = "smtp.mail.yahoo.com"
SMTP_PORT = 587
EMAIL_USER = "james.zulu35@yahoo.co.uk"
EMAIL_PASS = "your_yahoo_app_password"

# === LOGGING ===
logging.basicConfig(filename="usbwatch_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

# === EMAIL ALERT ===
def send_email_alert(subject, body):
    try:
        msg = EmailMessage()
        msg["From"] = EMAIL_USER
        msg["To"] = ADMIN_EMAIL
        msg["Subject"] = subject
        msg.set_content(body)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
    except Exception as e:
        logging.error(f"Email send failed: {e}")

# === PHANTOMSTAFF INTEGRATION ===
def phantom_notify(event_msg):
    phantom_script = "phantom_autotalk.py"
    with open("phantom_msg.txt", "w") as f:
        f.write(event_msg)
    os.system(f"python {phantom_script}")

# === STEALTH PHOTO ===
def take_stealth_photo():
    try:
        cam = cv2.VideoCapture(0)
        ret, frame = cam.read()
        if ret:
            filename = "usb_event.jpg"
            cv2.imwrite(filename, frame)
            logging.info("Stealth photo taken.")
        cam.release()
        cv2.destroyAllWindows()
    except Exception as e:
        logging.error(f"Camera error: {e}")

# === REFRESH EXPLORER ===
def refresh_explorer():
    try:
        os.system("taskkill /f /im explorer.exe")
        time.sleep(1)
        os.system("start explorer.exe")
        logging.info("Windows Explorer refreshed.")
    except Exception as e:
        logging.error(f"Failed to refresh Explorer: {e}")

# === USB DRIVE CHECK ===
def get_removable_drives():
    drives = []
    drivebits = win32file.GetLogicalDrives()
    for d in range(1, 26):
        mask = 1 << d
        if drivebits & mask:
            drive_type = win32file.GetDriveType(f"{chr(65 + d)}:\\")
            if drive_type == win32file.DRIVE_REMOVABLE:
                drives.append(f"{chr(65 + d)}:\\")
    return set(drives)

# === ALERT + LOG ===
def handle_usb(drive):
    print(f"USB Drive Detected: {drive}")
    logging.info(f"USB inserted: {drive}")
    send_email_alert("USB ALERT", f"A USB drive was inserted: {drive}")
    phantom_notify(f"USB inserted on drive {drive}")
    take_stealth_photo()
    refresh_explorer()

# === MAIN MONITOR LOOP ===
def main():
    print("Monitoring USB ports...")
    previous = get_removable_drives()

    try:
        while True:
            time.sleep(2)
            current = get_removable_drives()
            inserted = current - previous
            removed = previous - current

            for drive in inserted:
                handle_usb(drive)

            for drive in removed:
                print(f"USB Drive Removed: {drive}")
                logging.info(f"USB removed: {drive}")

            previous = current
    except KeyboardInterrupt:
        print("Monitoring stopped.")
        logging.info("Monitoring stopped by user.")

if __name__ == "__main__":
    main()
