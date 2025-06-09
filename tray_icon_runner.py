
import time
import threading
from pystray import Icon, MenuItem as item
from PIL import Image
from win10toast import ToastNotifier

# Load tray icon image (must exist and be valid PNG)
icon_path = "SentinelIT_icon.png"
image = Image.open(icon_path)

# Set up the toast notifier
toaster = ToastNotifier()

def show_popup():
    while True:
        toaster.show_toast(
            "SentinelIT is Active",
            "System is protected and being monitored.",
            duration=60,
            threaded=True
        )
        time.sleep(300)  # Wait 5 minutes

def on_quit(icon, item):
    icon.stop()

# Set up the tray icon
menu = (item('Quit', on_quit),)
icon = Icon("SentinelIT", image, "SentinelIT", menu)

# Start the popup thread
popup_thread = threading.Thread(target=show_popup, daemon=True)
popup_thread.start()

# Run the tray icon
icon.run()
