import os, json, threading, psutil
from datetime import datetime, UTC
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, current_user, logout_user, UserMixin
from flask_mail import Mail, Message
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = 'your-secure-secret-key'

app.config.update({
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///sentinel.db',
    'MAIL_SERVER': 'smtp.gmail.com',
    'MAIL_PORT': 587,
    'MAIL_USE_TLS': True,
    'MAIL_USERNAME': 'zxolani74@gmail.com',
    'MAIL_PASSWORD': 'your-gmail-app-password',
    'MAIL_DEFAULT_SENDER': 'zxolani74@gmail.com'
})

db = SQLAlchemy(app)
mail = Mail(app)
socketio = SocketIO(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
serializer = URLSafeTimedSerializer(app.secret_key)
system_metrics = {}

# ---------- Models ----------
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(256))
    role = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))

class SystemEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(100))
    message = db.Column(db.String(300))
    timestamp = db.Column(db.DateTime, default=datetime.now(UTC))
    user_id = db.Column(db.Integer)

# ---------- Metrics Thread ----------
def update_metrics():
    while True:
        try:
            system_metrics.update({
                'cpu': psutil.cpu_percent(),
                'memory': psutil.virtual_memory().percent,
                'disk': psutil.disk_usage('/').percent,
                'sent': psutil.net_io_counters().bytes_sent,
                'recv': psutil.net_io_counters().bytes_recv,
                'timestamp': datetime.now(UTC).strftime("%H:%M:%S")
            })
            socketio.emit('metrics', system_metrics)
        except Exception as e:
            print("Metrics error:", e)

threading.Thread(target=update_metrics, daemon=True).start()

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
        raw = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, raw):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash("Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# @app.route('/dashboard')
@login_required
def dashboard():
    users = User.query.all()
    return render_template(
        'dashboard.html',
        user=current_user,
        users=users,
        system_metrics=system_metrics,
        datetime=datetime
    )

@app.route('/add_user', methods=['POST'])
@login_required
def add_user():
    if current_user.role != 'admin':
        return "Unauthorized", 403

    username = request.form['username']
    password = request.form['password']

    if not username or not password:
        return "Unauthorized", 403

    hashed_password = generate_password_hash(password, method='sha256')
    new_user = User(email=username, password=hashed_password, role='user')
    db.session.add(new_user)
    db.session.commit()

    event = SystemEvent(
        event_type='user_add',
        message=f"New user {username} added by {current_user.email}",
        user_id=current_user.id
    )
    db.session.add(event)
    db.session.commit()

    flash("✅ User added successfully!")
    return redirect(url_for('dashboard'))

@app.route('/system-metrics')
@login_required
def metrics_view():
    return jsonify(system_metrics)

# ---------- SocketIO ----------
@socketio.on('connect')
def handle_connect():
    emit('status', {'message': 'Connected to SentinelIT'})

@socketio.on('threat_detected')
def handle_threat(data):
    print("🔴 Threat:", data)
    emit('new_threat', data, broadcast=True)

# ---------- Database Setup ----------
with app.app_context():
    db.create_all()
    if not User.query.filter_by(email='admin@sentinel.com').first():
        admin = User(
            email='admin@sentinel.com',
            password=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Default admin initialized")

# ---------- Launch ----------
if __name__ == '__main__':
    print("🚀 SentinelIT running on http://localhost:5000")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)




