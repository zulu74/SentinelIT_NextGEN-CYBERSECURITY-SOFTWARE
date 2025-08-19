
import os
import threading

# Core modules
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
import watchdog_ai  # New Watchdog AI module
import pluginloader
import dashboard_server
import trayiconrunner
import selfmaintainer  # 🔁 Auto healing and patching module
import ftpwatch
import snmpguard
import cloudwatch   # Cloud Event Logger
import packetshield  # Network packet protection

from cloudwatch import start_cloudwatch  # <-- directly import correct entry

def launch(module, name, entry_point="start"):
    try:
        target = getattr(module, entry_point)
    except AttributeError:
        print(f"[Launcher] Module {name} has no entry point '{entry_point}'")
        return
    thread = threading.Thread(target=target, name=name)
    thread.daemon = True
    thread.start()
    print(f"[Launcher] Launched {name} ({entry_point})")

def run_self_maintainer_periodically():
    while True:
        try:
            selfmaintainer.self_heal_and_update()
        except Exception as e:
            print(f"[SelfMaintainer] Error: {e}")
        threading.Event().wait(6 * 3600)  # every 6 hours

if __name__ == "__main__":
    # Startup system check
    try:
        print("[SelfMaintainer] Running startup system integrity check...")
        selfmaintainer.self_heal_and_update()
    except Exception as e:
        print(f"[SelfMaintainer] Startup check failed: {e}")

    # Periodic self-check
    threading.Thread(target=run_self_maintainer_periodically, daemon=True).start()

    # Module launches
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
    launch(kernelwatch, "KernelWatch", entry_point="main")
    launch(memorywatch, "MemoryWatch", entry_point="main")
    launch(watchdog_ai, "WatchdogAI", entry_point="main")
    launch(pluginloader, "PluginLoader")
    launch(dashboard_server, "DashboardServer")
    launch(trayiconrunner, "TrayIconRunner")
    launch(ftpwatch, "FTPWatch")
    launch(snmpguard, "SNMPGuard")

    # Correct CloudWatch launch
    print("[Launcher] Launching CloudWatch...")
    threading.Thread(target=start_cloudwatch, name="CloudWatch", daemon=True).start()

    # PacketShield launch (kept as is)
    launch(packetshield, "PacketShield", entry_point="start")

    print("[SentinelIT] All modules launched successfully.")

