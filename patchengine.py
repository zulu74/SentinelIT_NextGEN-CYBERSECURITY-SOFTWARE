import datetime
import json

def run_patchengine():
    print("[PATCHENGINE] Simulating patch and vulnerability scan...")

    # Simulated list of installed software with versions
    installed_software = [
        {"name": "Apache Struts", "version": "2.3.15"},
        {"name": "OpenSSL", "version": "1.0.2"},
        {"name": "Tomcat", "version": "7.0.79"},
        {"name": "Windows Server", "version": "2016"},
        {"name": "Ivanti EPMM", "version": "11.4"}
    ]

    # Simulated CVE database
    cve_db = {
        "Apache Struts": [{"cve": "CVE-2017-5638", "fixed_in": "2.3.32"}],
        "OpenSSL": [{"cve": "CVE-2016-2107", "fixed_in": "1.1.1"}],
        "Tomcat": [{"cve": "CVE-2017-5647", "fixed_in": "8.5.14"}],
        "Ivanti EPMM": [{"cve": "CVE-2025-4427", "fixed_in": "11.5"}]
    }

    results = []

    for software in installed_software:
        name = software["name"]
        version = software["version"]
        vulns = cve_db.get(name, [])
        for vuln in vulns:
            if version < vuln["fixed_in"]:
                results.append({
                    "software": name,
                    "version": version,
                    "cve": vuln["cve"],
                    "status": "VULNERABLE",
                    "patch_required": vuln["fixed_in"]
                })

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report = {
        "timestamp": timestamp,
        "vulnerability_report": results
    }

    with open("logs/patch_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"[PATCHENGINE] Patch scan complete. Results saved to logs/patch_report.json")
