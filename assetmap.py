import platform, socket, os, json

def get_asset_info():
    asset_info = {
        "hostname": socket.gethostname(),
        "ip_address": socket.gethostbyname(socket.gethostname()),
        "os": platform.system(),
        "version": platform.version(),
        "architecture": platform.machine()
    }
    return asset_info

def save_asset_info(path="logs/asset_inventory.json"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(get_asset_info(), f, indent=4)

def run_assetmap():
    print("[ASSETMAP] Starting asset inventory scan...")
    save_asset_info()
    print("[ASSETMAP] Asset inventory saved to logs/asset_inventory.json\n")

# Optional test run if run directly
if __name__ == "__main__":
    run_assetmap()
