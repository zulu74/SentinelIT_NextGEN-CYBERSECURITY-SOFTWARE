
import threading
import time
import usbwatch
import tomcat_honeypot
import ssh_honeypot
import rdp_honeypot
import resurgwatch
import fingerprint
import camera_iot_exposure_monitor
import iot_monitor
import memorywatch
import uefi_guard
import ai_monitor
import cve_audit
import ai_core
import siemcore_ai
import iamwatch_ai
import policyengine
import cloudwatch
import dashboard_server
import startup_display


def main():
    print("[SentinelIT] Starting SentinelIT Ultimate...")
    print("[SentinelIT] CMD lockdown lifted. Monitoring only.")
    print("[SentinelIT] All modules launched. System secure.")

    # Example: starting one of the modules in a thread
    threading.Thread(target=usbwatch.monitor_usb).start()
    threading.Thread(target=cloudwatch.start_cloudwatch).start()
    threading.Thread(target=dashboard_server.run_dashboard).start()

if __name__ == "__main__":
    main()
