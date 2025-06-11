
# dashboard_server.py – Live AI Dashboard for SentinelIT (Phase 8)
from flask import Flask, render_template
import os

app = Flask(__name__)

LOG_FILES = {
    "SIEM Summary": "siem_summary_log.txt",
    "IAM Watch": "iamwatch_log.txt",
    "USB Watch": "usbwatch_log.txt",
    "PacketShield": "packetshield_log.txt",
    "Policy Engine": "policyengine_log.txt",
    "Cloud Watch": "cloudwatch_log.txt"
}

@app.route("/")
def home():
    logs = {}
    for name, path in LOG_FILES.items():
        if os.path.exists(path):
            with open(path, "r", errors="ignore") as f:
                lines = f.readlines()[-15:]
                logs[name] = lines[::-1]
        else:
            logs[name] = ["[No Data Available]"]
    return render_template("index.html", logs=logs)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
