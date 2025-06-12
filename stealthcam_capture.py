
# stealthcam_capture.py
import cv2
from datetime import datetime
import os

CAPTURE_DIR = "logs/stealth_captures"
os.makedirs(CAPTURE_DIR, exist_ok=True)

def capture_image():
    try:
        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            return "[StealthCam] ERROR: Cannot access webcam."

        ret, frame = cam.read()
        if ret:
            filename = datetime.now().strftime("%Y%m%d_%H%M%S") + ".jpg"
            path = os.path.join(CAPTURE_DIR, filename)
            cv2.imwrite(path, frame)
            cam.release()
            return f"[StealthCam] Capture saved: {path}"
        else:
            cam.release()
            return "[StealthCam] ERROR: Failed to capture image."
    except Exception as e:
        return f"[StealthCam] ERROR: {e}"

# Example:
# print(capture_image())
