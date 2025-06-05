
def run_flowtrap():
    print("[FLOWTRAP] Deploying honeypots and decoys...")
    decoys = ['fake_admin_portal', 'dummy_ftp_server']
    with open("logs/decoy.log", "w") as f:
        for d in decoys:
            f.write(f"Deployed: {d}\n")
