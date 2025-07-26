# ultimate_main.py – SentinelIT Module Orchestrator

import sys
import os
import threading
import usbwatch
import phantomstaff
import stealthcam
import lockdown
import quarantine
import mailwatch
import patchcheckv2
import siemcore
import resurgwatch
import powerwatch
import traveltrap_email
import patternengine
import threatdna
import iotmonitor
import kernelwatch
import memorywatch
import pluginloader
import dashboard_server
import trayiconrunner
import selfmaintainer  # 🔁 Auto healing and patching module
import ftpwatch
import snmpguard


def launch(module, name):
    thread = threading.Thread(target=module.start, name=name)
    thread.daemon = True
    thread.start()


def run_self_maintainer_periodically():
    while True:
        try:
            selfmaintainer.self_heal_and_update()
        except Exception as e:
            print(f"[SelfMaintainer] Error: {e}")
        threading.Event().wait(6 * 3600)


if __name__ == "__main__":
    # ✅ Startup system check
    try:
        print("[SelfMaintainer] Running startup system integrity check...")
        selfmaintainer.self_heal_and_update()
    except Exception as e:
        print(f"[SelfMaintainer] Startup check failed: {e}")

    # ✅ Periodic self-check
    threading.Thread(target=run_self_maintainer_periodically, daemon=True).start()

    # ✅ Module launches
    launch(usbwatch, "USBWatch")
    launch(phantomstaff, "PhantomStaff")
    launch(stealthcam, "StealthCam")
    launch(lockdown, "Lockdown")
    launch(quarantine, "Quarantine")
    launch(mailwatch, "MailWatch")
    launch(patchcheckv2, "PatchCheckV2")
    launch(siemcore, "SIEMCore")
    launch(resurgwatch, "ResurgWatch")
    launch(powerwatch, "PowerWatch")
    launch(traveltrap_email, "TravelTrapEmail")
    launch(patternengine, "PatternEngine")
    launch(threatdna, "ThreatDNA")
    launch(iotmonitor, "IoTMonitor")
    launch(kernelwatch, "KernelWatch")
    launch(memorywatch, "MemoryWatch")
    launch(pluginloader, "PluginLoader")
    launch(dashboard_server, "DashboardServer")
    launch(trayiconrunner, "TrayIconRunner")
    launch(ftpwatch, "FTPWatch")
    launch(snmpguard, "SNMPGuard")

    print("[SentinelIT] All modules launched successfully.")
