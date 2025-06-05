
import importlib
import traceback

def safe_import_and_run(module_name, function_name, display_name):
    try:
        module = importlib.import_module(module_name)
        func = getattr(module, function_name)
        print(f"[+] Starting {display_name}...")
        func()
    except Exception as e:
        print(f"[-] Failed to start {display_name}: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    modules_to_run = [
        ("scantrap", "run_scantrap", "ScanTrap"),
        ("bannertrap", "run_bannertrap", "BannerTrap"),
        ("honeytrap", "run_honeytrap", "HoneyTrap"),
        ("xsswatch", "run_xsswatch", "XSSWatch"),
        ("dnswatch", "run_dnswatch", "DNSWatch"),
        ("policyengine", "run_policyengine", "PolicyEngine"),
        ("patchengine", "run_patchengine", "PatchEngine"),
        ("reportgen", "run_reportgen", "Report Generator"),
        ("phantomstaff", "run_phantomstaff", "PhantomStaff"),
        ("usbwatch", "run_usbwatch", "USBWatch"),
        ("helpdesk", "run_helpdesk", "AI Helpdesk")
    ]

    for module_name, function_name, display_name in modules_to_run:
        safe_import_and_run(module_name, function_name, display_name)
