
import time
import threading
from pystray import Icon, MenuItem as item
from PIL import Image
from win10toast import ToastNotifier

# Load the tray icon image
icon_path = "sentinelit_icon_shield.jpg"
image = Image.open(icon_path)

toaster = ToastNotifier()

def show_popup():
    while True:
        toaster.show_toast("SentinelIT is Active",
                           "System is protected and being monitored.",
                           duration=60,  # stays for 1 minute
                           threaded=True)
        time.sleep(300)  # wait 5 minutes

def on_quit(icon, item):
    icon.stop()

# Set up the tray icon
icon = Icon("SentinelIT")
icon.icon = image
icon.title = "SentinelIT"
icon.menu = (item('Quit', on_quit),)

# Start the popup thread
popup_thread = threading.Thread(target=show_popup, daemon=True)
popup_thread.start()

# Run the tray icon
icon.run()
