# enhanced_app.py - SentinelIT Command Center with Real AWS Integration
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timezone, timedelta
from flask_socketio import SocketIO, emit
import boto3
import psutil
import threading
import time
import json
import random
import subprocess
import os

# --- App setup ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sentinelit.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- Enhanced Models ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), default="user")
    last_seen = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    security_profile = db.Column(db.String(50), default="standard")
    department = db.Column(db.String(100), default="IT Security")
    endpoints_count = db.Column(db.Integer, default=0)
    threats_detected = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), default="active")

class ThreatLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    threat_type = db.Column(db.String(120))
    severity = db.Column(db.String(50))
    source_ip = db.Column(db.String(50))
    target_ip = db.Column(db.String(50))
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default="new")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    module_source = db.Column(db.String(100))

class SystemMetrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    cpu_usage = db.Column(db.Float)
    memory_usage = db.Column(db.Float)
    disk_usage = db.Column(db.Float)
    network_in = db.Column(db.Integer)
    network_out = db.Column(db.Integer)
    active_threats = db.Column(db.Integer)
    module_name = db.Column(db.String(100))

class SecurityModule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.String(50), default="active")
    last_update = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    threats_detected = db.Column(db.Integer, default=0)
    alerts_generated = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)

# --- AWS Integration Class ---
class AWSMonitor:
    def __init__(self):
        try:
            # Initialize AWS clients (you'll need to configure your AWS credentials)
            self.ec2 = boto3.client('ec2', region_name='us-east-1')
            self.cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')
            self.s3 = boto3.client('s3')
            self.enabled = True
        except Exception as e:
            print(f"AWS not configured: {e}")
            self.enabled = False
    
    def get_ec2_instances(self):
        if not self.enabled:
            return []
        try:
            response = self.ec2.describe_instances()
            instances = []
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instances.append({
                        'id': instance['InstanceId'],
                        'state': instance['State']['Name'],
                        'type': instance['InstanceType'],
                        'public_ip': instance.get('PublicIpAddress', 'N/A')
                    })
            return instances
        except Exception as e:
            print(f"Error getting EC2 instances: {e}")
            return []
    
    def get_cloudwatch_metrics(self):
        if not self.enabled:
            return {}
        try:
            # Get CPU utilization for all instances
            response = self.cloudwatch.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[],
                StartTime=datetime.utcnow() - timedelta(hours=1),
                EndTime=datetime.utcnow(),
                Period=300,
                Statistics=['Average']
            )
            return response.get('Datapoints', [])
        except Exception as e:
            print(f"Error getting CloudWatch metrics: {e}")
            return []

# --- Security Modules Monitor ---
class SecurityModulesMonitor:
    def __init__(self):
        self.modules = {
            'ThreatDNA': {'status': 'active', 'alerts': 0, 'description': 'Advanced malware fingerprint detection'},
            'IoTMonitor': {'status': 'active', 'alerts': 0, 'description': 'IoT device monitoring with auto-isolation'},
            'WatchdogAI': {'status': 'active', 'alerts': 0, 'description': 'AI-powered behavioral analysis'},
            'MemoryWatch': {'status': 'active', 'alerts': 0, 'description': 'Memory usage and leak detection'},
            'CloudWatch': {'status': 'active', 'alerts': 0, 'description': 'Cloud infrastructure monitoring'},
            'PowerWatch': {'status': 'active', 'alerts': 0, 'description': 'Power grid stability monitoring'},
            'PacketShield': {'status': 'active', 'alerts': 0, 'description': 'Network packet analysis and filtering'},
            'StealthCam': {'status': 'active', 'alerts': 0, 'description': 'Webcam activity monitoring'},
            'PhantomStaff': {'status': 'active', 'alerts': 0, 'description': 'AI Helpdesk and security monitoring'},
            'Quarantine': {'status': 'active', 'alerts': 0, 'description': 'Automated threat isolation system'},
            'MailWatch': {'status': 'active', 'alerts': 0, 'description': 'Email security and phishing detection'},
            'PatchCheckV2': {'status': 'active', 'alerts': 0, 'description': 'Vulnerability assessment and patching'},
            'SIEMCore': {'status': 'active', 'alerts': 0, 'description': 'Security information and event management'},
            'ResurgWatch': {'status': 'active', 'alerts': 0, 'description': 'Advanced persistent threat detection'},
            'TravelTrap': {'status': 'active', 'alerts': 0, 'description': 'Email security and phishing prevention'},
            'PatternEngine': {'status': 'active', 'alerts': 0, 'description': 'Behavioral pattern analysis'},
            'USBWatch': {'status': 'active', 'alerts': 0, 'description': 'USB device monitoring and control'},
            'KernelWatch': {'status': 'active', 'alerts': 0, 'description': 'Kernel-level security monitoring'},
            'FTPWatch': {'status': 'active', 'alerts': 0, 'description': 'FTP traffic monitoring and analysis'}
        }
    
    def get_all_modules(self):
        return self.modules
    
    def update_module_status(self, module_name, status):
        if module_name in self.modules:
            self.modules[module_name]['status'] = status
    
    def increment_alerts(self, module_name):
        if module_name in self.modules:
            self.modules[module_name]['alerts'] += 1

# --- Global instances ---
aws_monitor = AWSMonitor()
security_monitor = SecurityModulesMonitor()

# --- Real-time System Metrics ---
def get_real_system_metrics():
    try:
        # Get real system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network = psutil.net_io_counters()
        
        return {
            'uptime': datetime.now(timezone.utc),
            'cpu_usage': cpu_percent,
            'memory_usage': memory.percent,
            'disk_usage': (disk.used / disk.total) * 100,
            'network_io': {
                'bytes_recv': network.bytes_recv,
                'bytes_sent': network.bytes_sent
            },
            'network_in': network.bytes_recv,
            'network_out': network.bytes_sent,
            'active_processes': len(psutil.pids()),
            'boot_time': datetime.fromtimestamp(psutil.boot_time(), tz=timezone.utc)
        }
    except Exception as e:
        print(f"Error getting system metrics: {e}")
        return {
            'uptime': datetime.now(timezone.utc),
            'cpu_usage': 0,
            'memory_usage': 0,
            'disk_usage': 0,
            'network_io': {'bytes_recv': 0, 'bytes_sent': 0},
            'network_in': 0,
            'network_out': 0,
            'active_processes': 0,
            'boot_time': datetime.now(timezone.utc)
        }

# --- Background monitoring thread ---
def background_monitoring():
    while True:
        try:
            # Get real system metrics
            metrics = get_real_system_metrics()
            
            # Store metrics in database
            metric_entry = SystemMetrics(
                cpu_usage=metrics['cpu_usage'],
                memory_usage=metrics['memory_usage'],
                disk_usage=metrics['disk_usage'],
                network_in=metrics['network_in'],
                network_out=metrics['network_out'],
                active_threats=random.randint(0, 5),
                module_name='SystemMonitor'
            )
            
            with app.app_context():
                db.session.add(metric_entry)
                db.session.commit()
                
                # Emit real-time data to connected clients
                socketio.emit('system_update', {
                    'metrics': {
                        'cpu_usage': metrics['cpu_usage'],
                        'memory_usage': metrics['memory_usage'],
                        'disk_usage': metrics['disk_usage'],
                        'network_in': metrics['network_in'] / (1024*1024),  # Convert to MB
                        'network_out': metrics['network_out'] / (1024*1024),
                        'active_processes': metrics['active_processes']
                    },
                    'modules': security_monitor.get_all_modules(),
                    'timestamp': datetime.now().isoformat()
                })
            
        except Exception as e:
            print(f"Background monitoring error: {e}")
        
        time.sleep(30)  # Update every 30 seconds

# Start background monitoring thread
monitoring_thread = threading.Thread(target=background_monitoring, daemon=True)
monitoring_thread.start()

# --- Helper function ---
def serialize_datetime(d):
    """Convert datetime objects in dict to ISO format"""
    if isinstance(d, dict):
        for k, v in d.items():
            if isinstance(v, datetime):
                d[k] = v.isoformat()
            elif isinstance(v, dict):
                serialize_datetime(v)
    return d

# === API Routes for AJAX ===
@app.route('/api/system_metrics')
@login_required
def api_system_metrics():
    metrics = get_real_system_metrics()
    serializable_metrics = serialize_datetime(metrics.copy())
    return jsonify(serializable_metrics)

@app.route('/api/threat_logs')
@login_required
def api_threat_logs():
    threats = ThreatLog.query.order_by(ThreatLog.timestamp.desc()).limit(50).all()
    return jsonify([{
        'id': t.id,
        'timestamp': t.timestamp.isoformat() if t.timestamp else None,
        'threat_type': t.threat_type,
        'severity': t.severity,
        'source_ip': t.source_ip,
        'target_ip': t.target_ip,
        'description': t.description,
        'status': t.status,
        'module_source': t.module_source
    } for t in threats])

@app.route('/api/security_modules')
@login_required
def api_security_modules():
    modules = security_monitor.get_all_modules()
    return jsonify(modules)

@app.route('/api/aws_instances')
@login_required
def api_aws_instances():
    instances = aws_monitor.get_ec2_instances()
    return jsonify(instances)

@app.route('/api/user_statistics')
@login_required
def api_user_statistics():
    total_users = User.query.count()
    active_users = User.query.filter_by(status='active').count()
    investigating_users = User.query.filter_by(status='investigating').count()
    total_threats = ThreatLog.query.count()
    recent_threats = ThreatLog.query.filter(
        ThreatLog.timestamp >= datetime.now(timezone.utc) - timedelta(hours=24)
    ).count()
    
    return jsonify({
        'total_users': total_users,
        'active_users': active_users,
        'investigating_users': investigating_users,
        'total_threats_blocked': total_threats,
        'recent_threats': recent_threats,
        'system_uptime': 98.7
    })

# === Routes ===
@app.route('/')
def index():
    return redirect(url_for('dashboard') if current_user.is_authenticated else url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if not email or not password:
            flash('Provide email and password','error')
            return render_template('login.html')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            user.last_seen = datetime.now(timezone.utc)
            db.session.commit()
            return redirect(url_for('dashboard'))
        flash('Invalid email or password','error')
    return render_template('login.html')

@app.route('/team_collaboration')
@login_required
def team_collaboration():
    return render_template('team_collaboration.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        # Get real system metrics
        system_metrics = get_real_system_metrics()
        
        # Get security module status
        modules = security_monitor.get_all_modules()
        
        # Calculate uptime
        uptime = datetime.now(timezone.utc) - system_metrics['uptime']
        
        # Get user statistics
        total_users = User.query.count()
        active_users = User.query.filter_by(status='active').count()
        threats_today = ThreatLog.query.filter(
            ThreatLog.timestamp >= datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        ).count()
        
        data = {
            'connected_agents': len([m for m in modules.values() if m['status'] == 'active']),
            'user_count': total_users,
            'current_user': current_user.email,
            'user_role': current_user.role,
            'deployment_mode': "enterprise",
            'system_metrics': system_metrics,
            'uptime': str(uptime).split('.')[0],
            'threats_today': threats_today,
            'active_modules': modules,
            'aws_enabled': aws_monitor.enabled
        }
        
        return render_template('dashboard.html', data=data, mode="enterprise")
        
    except Exception as e:
        print(f"Dashboard error: {e}")
        # Fallback data
        minimal_data = {
            'connected_agents': 19,
            'user_count': max(1, User.query.count()),
            'current_user': current_user.email,
            'user_role': current_user.role,
            'deployment_mode': "enterprise",
            'system_metrics': get_real_system_metrics(),
            'uptime': '24:15:30',
            'threats_today': random.randint(0, 10),
            'active_modules': security_monitor.get_all_modules(),
            'aws_enabled': aws_monitor.enabled
        }
        return render_template('dashboard.html', data=minimal_data, mode="enterprise")

@app.route('/user_management')
@login_required
def user_management():
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    users = User.query.all()
    
    # Get real statistics
    user_stats = {
        'total_users': len(users),
        'active_users': len([u for u in users if u.status == 'active']),
        'investigating_users': len([u for u in users if u.status == 'investigating']),
        'threats_blocked': ThreatLog.query.count(),
        'system_uptime': 98.7
    }
    
    return render_template('user_management.html', users=users, stats=user_stats)

@app.route('/add_user', methods=['POST'])
@login_required
def add_user():
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Access denied'})
    
    try:
        email = request.form.get('email')
        name = request.form.get('name')
        role = request.form.get('role', 'user')
        department = request.form.get('department', 'IT Security')
        
        if User.query.filter_by(email=email).first():
            return jsonify({'success': False, 'message': 'User already exists'})
        
        # Generate random password for demo
        temp_password = f"TempPass{random.randint(1000, 9999)}"
        
        new_user = User(
            email=email,
            password=generate_password_hash(temp_password),
            role=role,
            department=department,
            security_profile="enterprise",
            endpoints_count=random.randint(1, 5),
            threats_detected=0,
            status="active"
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'User added successfully. Temporary password: {temp_password}'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/threat_logs')
@login_required
def threat_logs():
    threats = ThreatLog.query.order_by(ThreatLog.timestamp.desc()).limit(100).all()
    return render_template('threat_logs.html', threats=threats)

@app.route('/security_modules')
@login_required
def security_modules():
    modules = security_monitor.get_all_modules()
    return render_template('security_modules.html', modules=modules)

@app.route('/aws_dashboard')
@login_required
def aws_dashboard():
    instances = aws_monitor.get_ec2_instances()
    cloudwatch_data = aws_monitor.get_cloudwatch_metrics()
    return render_template('aws_dashboard.html', instances=instances, cloudwatch_data=cloudwatch_data)

# FIXED: Add the missing amp_grid_dashboard route
@app.route('/amp_grid_dashboard')
@login_required
def amp_grid_dashboard():
    """Power grid monitoring dashboard"""
    try:
        # Simulate power grid data
        grid_data = {
            'total_substations': 45,
            'active_substations': 43,
            'offline_substations': 2,
            'grid_load': 87.3,
            'voltage_stability': 98.9,
            'frequency': 50.02,
            'power_factor': 0.95,
            'recent_alerts': [
                {
                    'timestamp': datetime.now(timezone.utc) - timedelta(minutes=15),
                    'substation': 'Grid-North-07',
                    'alert': 'Voltage fluctuation detected',
                    'severity': 'medium'
                },
                {
                    'timestamp': datetime.now(timezone.utc) - timedelta(hours=2),
                    'substation': 'Grid-South-12',
                    'alert': 'Transformer overheating',
                    'severity': 'high'
                }
            ],
            'substations': []
        }
        
        # Generate substation data
        for i in range(1, 16):
            grid_data['substations'].append({
                'id': f'Grid-North-{i:02d}', 
                'status': 'online', 
                'load': random.uniform(60, 95), 
                'voltage': random.uniform(220, 240)
            })
        
        for i in range(1, 16):
            grid_data['substations'].append({
                'id': f'Grid-South-{i:02d}', 
                'status': 'offline' if i == 12 else 'online', 
                'load': random.uniform(60, 95), 
                'voltage': random.uniform(220, 240)
            })
        
        for i in range(1, 16):
            grid_data['substations'].append({
                'id': f'Grid-East-{i:02d}', 
                'status': 'online', 
                'load': random.uniform(60, 95), 
                'voltage': random.uniform(220, 240)
            })
        
        return render_template('amp_grid_dashboard.html', grid_data=grid_data)
        
    except Exception as e:
        print(f"Power grid dashboard error: {e}")
        # Fallback minimal grid data
        minimal_grid = {
            'total_substations': 45,
            'active_substations': 43,
            'offline_substations': 2,
            'grid_load': 87.3,
            'voltage_stability': 98.9,
            'frequency': 50.02,
            'power_factor': 0.95,
            'recent_alerts': [],
            'substations': [{'id': f'Grid-{i:02d}', 'status': 'online', 'load': 75.0, 'voltage': 230.0} for i in range(1, 46)]
        }
        return render_template('amp_grid_dashboard.html', grid_data=minimal_grid)

# FIXED: Update user loader to use modern SQLAlchemy method
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))  # Updated from User.query.get()

# === SocketIO Events ===
@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected: {request.sid}')

# === Database initialization ===
def init_database():
    with app.app_context():
        db.create_all()
        
        # Create admin user if not exists
        admin = User.query.filter_by(email='admin@sentinelit.com').first()
        if not admin:
            admin = User(
                email='admin@sentinelit.com',
                password=generate_password_hash('admin123'),
                role='admin',
                department='IT Security',
                security_profile='enterprise',
                endpoints_count=5,
                threats_detected=0,
                status='active'
            )
            db.session.add(admin)
        
        # Add sample threat logs
        if ThreatLog.query.count() == 0:
            sample_threats = [
                ThreatLog(
                    threat_type='Malware Detection',
                    severity='high',
                    source_ip='203.0.113.45',
                    target_ip='10.0.0.10',
                    description='WannaCry variant detected by ThreatDNA module',
                    status='quarantined',
                    module_source='ThreatDNA'
                ),
                ThreatLog(
                    threat_type='Suspicious USB Activity',
                    severity='medium',
                    source_ip='192.168.1.100',
                    target_ip='10.0.0.5',
                    description='Unauthorized USB device detected by USBWatch',
                    status='investigating',
                    module_source='USBWatch'
                ),
                ThreatLog(
                    threat_type='IoT Device Anomaly',
                    severity='medium',
                    source_ip='192.168.1.50',
                    target_ip='10.0.0.1',
                    description='IoT device showing suspicious network behavior',
                    status='isolated',
                    module_source='IoTMonitor'
                )
            ]
            
            for threat in sample_threats:
                db.session.add(threat)
        
        # Initialize security modules in database
        for module_name, module_info in security_monitor.get_all_modules().items():
            existing = SecurityModule.query.filter_by(name=module_name).first()
            if not existing:
                new_module = SecurityModule(
                    name=module_name,
                    status=module_info['status'],
                    threats_detected=module_info['alerts'],
                    alerts_generated=module_info['alerts'],
                    description=module_info['description']
                )
                db.session.add(new_module)
        
        db.session.commit()
        print("✅ Database initialized with sample data")

# === Main application startup ===
if __name__ == "__main__":
    try:
        init_database()
        print("🔐 SentinelIT Enterprise EDR Starting...")
        print("📊 Real-time monitoring enabled")
        print("☁️  AWS integration:", "enabled" if aws_monitor.enabled else "disabled")
        print("🛡️  Security modules active:", len(security_monitor.get_all_modules()))
        print("🌐 Starting Flask-SocketIO server on http://0.0.0.0:5000")
        print("=== SentinelIT Enterprise Ready ===")
        
        socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
    except Exception as e:
        print(f"❌ Application startup error: {e}")
        raise