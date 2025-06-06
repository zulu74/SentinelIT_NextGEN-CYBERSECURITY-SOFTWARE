
import time
import threading
from pystray import Icon, MenuItem as item
from PIL import Image
from win10toast import ToastNotifier

# Load the tray icon image
image = Image.open("SentinelIT_icon.png")

# Create the notifier
toaster = ToastNotifier()

def show_popup():
    while True:
        toaster.show_toast("SentinelIT is Active",
                           "System is protected and being monitored.",
                           duration=60,
                           threaded=True)
        time.sleep(300)  # Show every 5 minutes

def on_quit(icon, item):
    icon.stop()

# Setup tray icon
icon = Icon("SentinelIT")
icon.icon = image
icon.title = "SentinelIT"
icon.menu = (item("Quit", on_quit),)

# Start popup thread
popup_thread = threading.Thread(target=show_popup, daemon=True)
popup_thread.start()

# Run tray icon
icon.run()
