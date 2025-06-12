
# cve_decoy_trap.py
import os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

LOG_FILE = "logs/cve_decoy_trap_log.txt"
PORT = 8888

os.makedirs("logs", exist_ok=True)

known_cve_payloads = [
    "id=", "cmd=", "exec", "eval(", "file=", "shell", "ping", "wget", "curl", "nc ",
    "powershell", "python", "base64", "phpinfo", "/etc/passwd", "0x41414141", "sleep("
]

def log_decoy_event(ip, path, agent):
    with open(LOG_FILE, "a") as log:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log.write(f"[{timestamp}] IP: {ip}, Path: {path}, Agent: {agent}\n")

class CVEDecoyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        attacker_ip = self.client_address[0]
        agent = self.headers.get("User-Agent", "Unknown")
        suspicious = any(keyword in self.path.lower() for keyword in known_cve_payloads)

        if suspicious:
            log_decoy_event(attacker_ip, self.path, agent)

        self.send_response(403 if suspicious else 200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(b"<html><body><h3>Forbidden</h3></body></html>" if suspicious else b"<html><body><h3>OK</h3></body></html>")

def start_cve_decoy():
    print(f"[CVE Decoy Trap] Running on port {PORT}...")
    server = HTTPServer(("0.0.0.0", PORT), CVEDecoyHandler)
    server.serve_forever()

# Uncomment below to run standalone
# if __name__ == "__main__":
#     start_cve_decoy()
