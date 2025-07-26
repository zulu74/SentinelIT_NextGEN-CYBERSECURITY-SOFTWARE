from flask import Flask, jsonify, render_template
from threading import Thread
import random
import time
import datetime

app = Flask(__name__)

# Simulated memory of events for the dashboard
event_log = []

# Sample event generator for demo (can be replaced with real feeds)
def generate_threat_events():
    source_ips = ["10.0.0.1", "10.0.0.2", "10.0.0.3", "192.168.1.10"]
    destination_ips = ["10.0.24.2", "10.0.24.100", "172.17.85.5", "8.8.8.8"]
    files = ["trojan.exe", "exploit.js", "malware.pdf", "keylogger.zip"]
    types = ["Malware Event Record", "Host Timeout", "Unauthorized Access", "Phishing Attempt"]

    while True:
        event = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source_ip": random.choice(source_ips),
            "destination_ip": random.choice(destination_ips),
            "file": random.choice(files),
            "type": random.choice(types)
        }
        event_log.append(event)
        if len(event_log) > 100:
            event_log.pop(0)
        time.sleep(5)  # simulate 1 event every 5 seconds

# Route for main threat dashboard
@app.route("/threats")
def threat_dashboard():
    return render_template("threat_dashboard.html")

# API endpoint to serve event data
@app.route("/api/threats")
def api_threat_data():
    return jsonify(event_log)

if __name__ == "__main__":
    Thread(target=generate_threat_events, daemon=True).start()
    app.run(debug=True, port=5000)
