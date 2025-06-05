
import threading
import time

def safe_import_and_run(module_name, function_name):
    try:
        module = __import__(module_name)
        func = getattr(module, function_name)
        thread = threading.Thread(target=func)
        thread.daemon = True
        thread.start()
        print(f"[✓] {module_name} started.")
    except Exception as e:
        print(f"[!] Failed to start {module_name}: {e}")

modules_to_run = [
    ("main", "run_main"),
    ("usbwatch", "run_usbwatch"),
    ("xsswatch", "run_xsswatch"),
    ("dnswatch", "run_dnswatch"),
    ("resurgwatch", "run_resurgwatch"),
    ("phantomstaff", "run_phantomstaff"),
    ("patchengine", "run_patchengine"),
    ("policyengine", "run_policyengine"),
    ("reportgen", "run_reportgen"),
    ("scantrap", "run_scantrap"),
    ("bannertrap", "run_bannertrap"),
    ("honeytrap", "run_honeytrap"),
    ("mailwatch", "run_mailwatch"),
    ("lockdown", "run_lockdown"),
    ("trapengine", "run_trapengine"),
    ("honeypot", "run_honeypot"),
    ("casewatch", "run_casewatch"),
    ("pluginloader", "run_pluginloader"),
    ("patternengine", "run_patternengine"),
    ("siemcore", "run_siemcore"),
    ("threatdna", "run_threatdna"),
]

if __name__ == "__main__":
    print("[*] Starting SentinelIT AutoExec...")
    for module, function in modules_to_run:
        safe_import_and_run(module, function)
    print("[✓] All modules launched. SentinelIT is live.")
    while True:
        time.sleep(5)
