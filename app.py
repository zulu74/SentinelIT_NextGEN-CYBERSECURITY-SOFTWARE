import os
import json
import threading
from datetime import datetime, UTC
import psutil
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.secret_key = 'your-secure-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sentinel.db'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'zxolani74@gmail.com'
app.config['MAIL_PASSWORD'] = 'your-gmail-app-password'
app.config['MAIL_DEFAULT_SENDER'] = 'zxolani74@gmail.com'

db = SQLAlchemy(app)
mail = Mail(app)
login_manager = LoginManager(app)
serializer = URLSafeTimedSerializer(app.secret_key)
socketio = SocketIO(app)
system_metrics = {}

# ---------- Models ----------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))
    is_connected = db.Column(db.Boolean, default=False)

class SystemEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(100))
    message = db.Column(db.String(300))
    timestamp = db.Column(db.DateTime, default=datetime.now(UTC))
    user_id = db.Column(db.Integer)

# ---------- Security Modules ----------
class SecurityModule:
    def __init__(self, name):
        self.name = name
        self.status = 'enabled'
        self.last_update = datetime.now(UTC)

    def toggle(self):
        self.status = 'disabled' if self.status == 'enabled' else 'enabled'
        self.last_update = datetime.now(UTC)

auth = SecurityModule('auth')
packetcheck = SecurityModule('packetcheck')
vaultwatch = SecurityModule('vaultwatch')

# ---------- System Monitoring ----------
def update_system_metrics():
    while True:
        try:
            system_metrics['cpu'] = psutil.cpu_percent()
            system_metrics['memory'] = psutil.virtual_memory().percent
            system_metrics['disk'] = psutil.disk_usage('/').percent
            net = psutil.net_io_counters()
            system_metrics['net_sent'] = net.bytes_sent
            system_metrics['net_recv'] = net.bytes_recv
            system_metrics['timestamp'] = datetime.now(UTC).strftime("%H:%M:%S")
        except Exception as e:
            print(f"[Metrics Error]: {str(e)}")

def start_monitoring():
    threading.Thread(target=update_system_metrics, daemon=True).start()

# ---------- Auth ----------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        raw_password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, raw_password):
            login_user(user)
            user.is_connected = True
            db.session.commit()
            event = SystemEvent(event_type='login', message=f"{email} logged in", user_id=user.id)
            db.session.add(event)
            db.session.commit()
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    event = SystemEvent(event_type='logout', message=f"{current_user.email} logged out", user_id=current_user.id)
    db.session.add(event)
    db.session.commit()
    current_user.is_connected = False
    db.session.commit()
    logout_user()
    return redirect(url_for('login'))

# ---------- Dashboard & Users ----------
@app.route('/dashboard')
@login_required
def dashboard():
    current_user.last_seen = datetime.now(UTC)
    db.session.commit()
    user_list = User.query.all()
    return render_template('dashboard.html', user=current_user, users=user_list, system_metrics=system_metrics, modules=[auth, packetcheck, vaultwatch])

@app.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.role != 'admin':
        return "Unauthorized", 403
    if request.method == 'POST':
        email = request.form['email']
        raw_password = request.form['password']
        role = request.form['role']
        hashed = generate_password_hash(raw_password)
        new_user = User(email=email, password=hashed, role=role)
        db.session.add(new_user)
        db.session.commit()

        token = serializer.dumps(email, salt='enroll-token')
        link = url_for('enroll', token=token, _external=True)
        msg = Message("Welcome to SentinelIT", recipients=[email])
        msg.body = f"""Hi {email},

Welcome to SentinelIT.
Click to complete your enrollment: {link}

SentinelIT Command Team"""
        try:
            mail.send(msg)
            flash("User added and email sent.")
        except Exception as e:
            flash(f"Mail error: {str(e)}")
        return redirect(url_for('dashboard'))

    return render_template('add_user.html')

@app.route('/users')
@login_required
def users():
    if current_user.role != 'admin':
        return "Unauthorized", 403
    user_list = User.query.all()
    return jsonify([
        {
            'email': u.email,
            'role': u.role,
            'connected': u.is_connected,
            'created_at': u.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for u in user_list
    ])

@app.route('/enroll/<token>')
def enroll(token):
    try:
        email = serializer.loads(token, salt='enroll-token', max_age=3600)
        return f"Enrollment page for {email}"
    except:
        return "Invalid or expired link", 403

# ---------- Metrics & Threats ----------
@app.route('/system-metrics')
@login_required
def system_metrics_view():
    return jsonify(system_metrics)

@app.route('/threat-events')
@login_required
def threat_events():
    path = os.path.join("threat_logs", datetime.now(UTC).strftime("%Y-%m-%d"), "events.json")
    try:
        with open(path, "r") as f:
            return jsonify(json.load(f))
    except:
        return jsonify([])

# ---------- SocketIO ----------
@socketio.on('connect')
def handle_connect():
    emit('status', {'message': 'SentinelIT connection established'})

@socketio.on('threat_detected')
def handle_threat(data):
    print("Threat received:", data)
    emit('new_threat', data, broadcast=True)

# ---------- Database Reset ----------
with app.app_context():
    db.create_all()
    if not User.query.filter_by(email='admin@sentinel.com').first():
        admin = User(
            email='admin@sentinel.com',
            password=generate_password_hash('admin123'),
            role='admin',
            created_at=datetime.now(UTC)
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Default admin created")

start_monitoring()

# ---------- App Launch ----------
if __name__ == '__main__':
    print("🚀 SentinelIT Launching at http://localhost:5000")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)