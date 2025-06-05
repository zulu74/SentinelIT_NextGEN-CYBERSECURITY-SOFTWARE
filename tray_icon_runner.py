
import time
import threading
from pystray import Icon, MenuItem as item
from PIL import Image
from win10toast import ToastNotifier

# Load icon image (make sure the path is correct)
image = Image.open("SentinelIT_icon.jpg")

# Create toast notifier
toaster = ToastNotifier()

# Function to show periodic notifications
def show_popup():
    while True:
        toaster.show_toast(
            "SentinelIT is Active",
            "System is protected and being monitored.",
            duration=60,  # 1 minute
            threaded=True
        )
        time.sleep(300)  # 5 minutes

# Function to quit tray icon
def on_quit(icon, item):
    icon.stop()

# Define tray icon
icon = Icon("SentinelIT")
icon.icon = image
icon.title = "SentinelIT"
icon.menu = (item('Quit', on_quit),)

# Start popup thread
thread = threading.Thread(target=show_popup, daemon=True)
thread.start()

# Start tray icon (this is what shows it!)
icon.run()

