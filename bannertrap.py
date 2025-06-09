def run_bannertrap():
    print("[BANNERTRAP] Deploying fake service banners...")

    fake_banners = {
        "SSH": "OpenSSH_3.9p1 Debian-1ubuntu2.1",
        "HTTP": "Apache/1.3.26 (Unix)",
        "FTP": "vsFTPd 2.0.1",
        "SMTP": "Sendmail 8.13.8/8.13.8",
        "RDP": "Microsoft Terminal Services 5.1"
    }

    with open("logs/bannertrap.log", "w") as f:
        for service, banner in fake_banners.items():
            line = f"[{service}] Fake Banner: {banner}\n"
            f.write(line)

    print("[BANNERTRAP] Banners deployed and logged.")
