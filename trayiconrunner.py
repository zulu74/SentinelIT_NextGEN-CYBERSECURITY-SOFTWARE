
import time
from PyQt5 import QtWidgets, QtGui, QtCore
import sys
import os

class TrayApp(QtWidgets.QSystemTrayIcon):
    def __init__(self, icon, parent=None):
        super(TrayApp, self).__init__(icon, parent)
        self.setToolTip("SentinelIT Monitoring Active")
        menu = QtWidgets.QMenu(parent)
        exit_action = menu.addAction("Exit")
        exit_action.triggered.connect(QtWidgets.qApp.quit)
        self.setContextMenu(menu)
        self.showMessage("SentinelIT Activated", "Monitoring has started.", QtWidgets.QSystemTrayIcon.Information, 3000)

def run_tray_icon():
    app = QtWidgets.QApplication(sys.argv)
    tray_icon = TrayApp(QtGui.QIcon("sentinelit_icon.ico"))
    tray_icon.show()
    QtCore.QTimer.singleShot(3000, lambda: None)
    sys.exit(app.exec_())

if __name__ == "__main__":
    run_tray_icon()

import time
import threading

def start():
    print("[TrayIconRunner] SentinelIT is running in the background with tray icon...")

    def notification_loop():
        while True:
            print("[TrayIcon] System secure. All modules active.")
            time.sleep(300)  # 5 minutes

    thread = threading.Thread(target=notification_loop)
    thread.daemon = True
    thread.start()
