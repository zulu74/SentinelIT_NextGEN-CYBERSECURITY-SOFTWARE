
# accessauth.py - SentinelIT Access Control Module (Modified)

def authorize_access():
    """
    This version of authorize_access does NOT block cmd or PowerShell.
    It simply logs the event and allows all access.
    """
    print("[AccessAuth] Access granted to CMD/PowerShell.")
    return True

def check_usb_policy():
    """
    This function now allows all USB access. In future, you can re-add checks.
    """
    print("[AccessAuth] USB access is allowed.")
    return True

if __name__ == "__main__":
    if authorize_access() and check_usb_policy():
        print("[AccessAuth] System policies allow access.")
    else:
        print("[AccessAuth] Access blocked by policy.")
