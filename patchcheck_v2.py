
import logging

log_path = "C:/opt/SentinelIT/logs/patchcheck_v2.log"
logging.basicConfig(filename=log_path, level=logging.INFO, format="%(asctime)s - %(message)s")

# Simulated CVE data
cve_data = {
    "openssl": {
        "version": "1.0.2",
        "cve": "CVE-2016-2107",
        "cvss": 9.8,
        "cisa_known": True
    }
}

def get_version(pkg):
    return "1.0.1"  # Simulate outdated version

def check(sim=False):
    for pkg, info in cve_data.items():
        inst = get_version(pkg)
        if inst <= info["version"]:
            msg = f"{pkg} vulnerable: {info['cve']} CVSS={info['cvss']} CISA={info['cisa_known']}"
            logging.warning(msg)
            if sim:
                print(msg)

def run():
    check(sim=True)
