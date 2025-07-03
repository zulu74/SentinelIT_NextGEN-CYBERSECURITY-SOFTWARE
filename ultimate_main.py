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
import vaultwatch
import traveltrap_email
import patternengine
import threatdna
import iotmonitor
import kernelwatch
import memorywatch
import pluginloader
import dashboard_server
import trayiconrunner




def launch(module, name):
    thread = threading.Thread(target=module.start, name=name)
    thread.daemon = True
    thread.start()

if __name__ == "__main__":
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
    launch(vaultwatch, "VaultWatch")
    launch(traveltrap_email, "TravelTrapEmail")
    launch(patternengine, "PatternEngine")
    launch(threatdna, "ThreatDNA")
    launch(iotmonitor, "IoTMonitor")
    launch(kernelwatch, "KernelWatch")
    launch(memorywatch, "MemoryWatch")
    launch(pluginloader, "PluginLoader")
    launch(dashboard_server, "DashboardServer")
    launch(trayiconrunner, "TrayIconRunner")
    
    

    print("[SentinelIT] All modules launched successfully.")
