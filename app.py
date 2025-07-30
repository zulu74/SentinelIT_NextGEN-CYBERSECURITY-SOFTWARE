import os
import threading
import psutil
from datetime import datetime, timezone
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, current_user, logout_user, UserMixin
from flask_mail import Mail, Message
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from threatreport import generate_computer_threats

# ---------- Flask App Setup ----------
app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = 'your-secure-secret-key'

# ---------- Configuration ----------
app.config.update({
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///sentinel.db',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'MAIL_SERVER': 'smtp.gmail.com',
    'MAIL_PORT': 587,
    'MAIL_USE_TLS': True,
    'MAIL_USERNAME': 'zxolani74@gmail.com',
    'MAIL_PASSWORD': 'your-gmail-app-password',
    'MAIL_DEFAULT_SENDER': 'zxolani74@gmail.com'
})

# ---------- Extensions ----------
db = SQLAlchemy(app)
mail = Mail(app)
socketio = SocketIO(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
serializer = URLSafeTimedSerializer(app.secret_key)
system_metrics = {}
latest_threats = []

# ---------- Models ----------
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), default='user')
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

class SystemEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(100))
    message = db.Column(db.String(300))
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    user_id = db.Column(db.Integer)

# ---------- Background System Metrics ----------
def update_metrics():
    while True:
        try:
            system_metrics.update({
                'cpu': psutil.cpu_percent(),
                'memory': psutil.virtual_memory().percent,
                'disk': psutil.disk_usage('/').percent,
                'sent': psutil.net_io_counters().bytes_sent,
                'recv': psutil.net_io_counters().bytes_recv,
                'timestamp': datetime.now(timezone.utc).strftime("%H:%M:%S")
            })
            socketio.emit('metrics', system_metrics)
        except Exception as e:
            print("⚠️ Metrics error:", e)

threading.Thread(target=update_metrics, daemon=True).start()

# ---------- Background Threat Simulation ----------
def simulate_threats():
    global latest_threats
    while True:
        try:
            latest_threats = generate_computer_threats()
            socketio.emit('threats', latest_threats)
        except Exception as e:
            print("⚠️ Threat simulation error:", e)
        socketio.sleep(10)

socketio.start_background_task(simulate_threats)

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
            return redirect(url_for('dashboard'))
        flash("❌ Invalid credentials", "danger")
    return render_template('login.html', now=datetime.utcnow)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    users = User.query.all()
    return render_template(
        'dashboard.html',
        user=current_user,
        users=users,
        system_metrics=system_metrics,
        threats=latest_threats,
        datetime_util=datetime,
        now=datetime.utcnow
    )

@app.route('/add_user', methods=['POST'])
@login_required
def add_user():
    if current_user.role != 'admin':
        return "Unauthorized", 403

    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        flash("⚠️ Missing username or password", "warning")
        return redirect(url_for('dashboard'))

    if User.query.filter_by(email=username).first():
        flash("⚠️ User already exists", "warning")
        return redirect(url_for('dashboard'))

    hashed_password = generate_password_hash(password)
    new_user = User(email=username, password=hashed_password)
    db.session.add(new_user)

    event = SystemEvent(
        event_type='user_add',
        message=f"New user {username} added by {current_user.email}",
        user_id=current_user.id
    )
    db.session.add(event)
    db.session.commit()

    flash("✅ User added successfully!", "success")
    return redirect(url_for('dashboard'))

@app.route('/system-metrics')
@login_required
def metrics_view():
    return jsonify(system_metrics)

@app.route('/download')
@login_required
def download_installer():
    return send_from_directory(directory='installers', filename='SentinelITInstaller.exe', as_attachment=True)

# ---------- Socket.IO Handlers ----------
@socketio.on('connect')
def handle_connect():
    emit('status', {'message': 'Connected to SentinelIT'})
    emit('metrics', system_metrics)
    emit('threats', latest_threats)

# ---------- Favicon ----------
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )

# ---------- DB Initialization ----------
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
        print("✅ Default admin account created")

# ---------- Run App ----------
if __name__ == '__main__':
    print("SentinelIT running on http://localhost:5000")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
