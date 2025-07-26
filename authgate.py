# authgate.py – SentinelIT Secondary Authentication Gate

import getpass

# ✅ Default hardcoded user credentials (you can later load from config or encrypted store)
AUTH_CREDENTIALS = {
    "ftp": {"username": "ftpadmin", "password": "Sentinel@123"},
    "snmp": {"username": "netadmin", "password": "SecureSNMP!"},
    "default": {"username": "admin", "password": "SentinelIT2025"}
}

class AuthGate:
    def authenticate(self, context="default"):
        print(f"\n[AuthGate] Secondary authentication required for: {context.upper()}")

        credentials = AUTH_CREDENTIALS.get(context, AUTH_CREDENTIALS["default"])
        username = input("Username: ").strip()
        password = getpass.getpass("Password: ")

        if username == credentials["username"] and password == credentials["password"]:
            print("[AuthGate] Access granted.")
            return True
        else:
            print("[AuthGate] Access denied.")
            return False
