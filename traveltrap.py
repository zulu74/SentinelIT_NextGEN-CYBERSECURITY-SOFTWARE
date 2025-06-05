
import re
import traveltrap_email

def is_phishing_redirect(url):
    redirect_patterns = [
        r'https:\/\/www\.google\.com\/travel\/clk\?.*pcurl=.*',
        r'https:\/\/bit\.ly\/.*',
        r'https:\/\/.*\.php\?u=http.*'
    ]
    for pattern in redirect_patterns:
        if re.search(pattern, url):
            return True
    return False

def extract_redirect_target(url):
    match = re.search(r'pcurl=(https?:\/\/[^\s&]+)', url)
    if match:
        return match.group(1)
    return url

def run():
    print("[START] Redirect Phishing Trap (Google /travel/clk)")
    print("[TravelTrap] Phishing Redirect Scanner Active.")

    urls = [
        "https://www.google.com/travel/clk?pc=token123&pcurl=https://malicious-site.com/login",
        "https://malicious-site.com/login",
        "https://bit.ly/3FakePhish",
        "https://facebook.com/l.php?u=http://evil.com"
    ]

    for url in urls:
        if is_phishing_redirect(url):
            redirect_target = extract_redirect_target(url)
            print(f"[ALERT] Potential phishing redirect detected: {url} -> {redirect_target}")
            try:
                traveltrap_email.send_phishing_alert(url, redirect_target)
            except Exception as e:
                print(f"[EMAIL ERROR] {e}")
        else:
            print(f"[CLEAN] URL appears safe: {url}")

    print("[DONE] Redirect Phishing Trap")
