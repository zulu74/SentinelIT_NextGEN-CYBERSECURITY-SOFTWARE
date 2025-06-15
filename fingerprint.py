
# Sample CVE fingerprint database
fingerprint_db = {
    "CVE-2020-0601": {
        "description": "CurveBall - Windows CryptoAPI Spoofing",
        "pattern": ["certificates", "spoof", "CryptoAPI"],
        "cvss": 8.2
    },
    "CVE-2021-34527": {
        "description": "PrintNightmare - Windows Print Spooler RCE",
        "pattern": ["print spooler", "RCE", "SYSTEM privileges"],
        "cvss": 8.8
    }
}

# Returns the full fingerprint database
def get_known_fingerprints():
    return fingerprint_db

# Returns only the fingerprint identifiers (keys)
def generate_fingerprint():
    return list(fingerprint_db.keys())
