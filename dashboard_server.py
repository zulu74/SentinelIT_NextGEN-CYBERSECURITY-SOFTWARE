# dashboard_server.py – SentinelIT Dashboard with Flask-SocketIO

from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO
import psutil
from datetime import datetime
import threading
import time

app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading')

# Simulated user
user_data = {
    "email": "admin@sentinelit.local",
    "role": "Admin"
}
users = [user_data]

def get_live_metrics():
    return {
        "cpu": psutil.cpu_percent(),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent,
        "sent": psutil.net_io_counters().bytes_sent,
        "recv": psutil.net_io_counters().bytes_recv,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# Routes
@app.route("/")
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", user=user_data, system_metrics=get_live_metrics(), now=datetime.now)

@app.route("/monitoring")
def monitoring():
    return "Monitoring page (placeholder)"

@app.route("/settings")
def settings():
    return "Settings page (placeholder)"

@app.route("/logout")
def logout():
    return redirect(url_for('dashboard'))

@app.route("/add_user", methods=["POST"])
def add_user():
    email = request.form.get("username")
    password = request.form.get("password")
    users.append({"email": email, "role": "User"})
    return redirect(url_for('dashboard'))

# Real-time metrics emitter
def background_metrics_loop():
    while True:
        socketio.emit("metrics", get_live_metrics())
        socketio.sleep(5)

@socketio.on('connect')
def on_connect():
    print("[Dashboard] Client connected.")
    socketio.start_background_task(target=background_metrics_loop)

# ✅ Required for integration with ultimate_main.py
def start():
    print("[DashboardServer] Launching dashboard...")
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)

# ✅ Standalone run
if __name__ == "__main__":
    start()

