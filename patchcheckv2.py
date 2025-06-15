
import platform

def get_installed_software():
    os_type = platform.system()
    if os_type == "Windows":
        # Simulated output for installed software on Windows
        return ["Google Chrome", "Mozilla Firefox", "Notepad++", "Python 3.11"]
    elif os_type == "Linux":
        # Simulated output for installed software on Linux
        return ["openssl", "apache2", "python3", "curl"]
    else:
        return []

def load_vulnerability_db():
    # Simulated CVE data
    return {
        "Google Chrome": "CVE-2024-0519",
        "Mozilla Firefox": "CVE-2024-12345",
        "Notepad++": "CVE-2023-2222",
        "Python 3.11": "CVE-2023-1234",
        "openssl": "CVE-2024-4444",
        "apache2": "CVE-2024-9999",
        "curl": "CVE-2024-2345"
    }
