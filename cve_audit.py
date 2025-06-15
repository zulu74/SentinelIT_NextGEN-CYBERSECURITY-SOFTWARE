from fingerprint import get_known_fingerprints
from patchcheckv2 import get_installed_software, load_vulnerability_db

def run_cve_audit():
    print("[CVE Audit] Starting system audit...")
    installed_software = get_installed_software()
    vulnerability_db = load_vulnerability_db()
    known_fingerprints = get_known_fingerprints()

    findings = []

    for software in installed_software:
        name = software.get('name')
        version = software.get('version')
        for cve_id, data in vulnerability_db.items():
            if name in data.get('product', []) and version in data.get('version', []):
                findings.append({
                    'cve_id': cve_id,
                    'software': name,
                    'version': version,
                    'description': data.get('description', ''),
                    'cvss': data.get('cvss', 'N/A'),
                    'remediation': data.get('remediation', 'No remediation available')
                })

    if findings:
        print(f"[CVE Audit] Found {len(findings)} vulnerabilities:")
        for finding in findings:
            print(f"  - CVE: {finding['cve_id']}, {finding['software']} {finding['version']}")
            print(f"    Severity: {finding['cvss']}")
            print(f"    Details: {finding['description']}")
            print(f"    Remediation: {finding['remediation']}")
    else:
        print("[CVE Audit] No known vulnerabilities found.")
