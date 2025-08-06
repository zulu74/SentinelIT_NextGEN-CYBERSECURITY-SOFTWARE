
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
import os
import time
import psutil
from datetime import datetime, timedelta
import threading
import json
import sqlite3

# Import AMP Thread Grid
try:
    from thread_grid import AMPThreadGrid, TaskPriority
    from thread_grid import (
        threat_scanner_handler, packet_analyzer_handler, vulnerability_scanner_handler,
        log_processor_handler, ai_analyzer_handler, network_monitor_handler
    )
    print("✅ Successfully imported AMP Thread Grid module")
except ImportError as e:
    print(f"❌ Failed to import thread_grid module: {e}")
    print("Please ensure thread_grid.py exists in the same directory")
    exit(1)

# === App Setup ===
app = Flask(__name__)
app.secret_key = 'sentinel-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# === Mail Config ===
app.config['MAIL_SERVER'] = 'mail.diakriszuluinvestmentsprojects.co.za'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'admin@diakriszuluinvestmentsprojects.co.za'
app.config['MAIL_PASSWORD'] = 'QE6TkRT2ms'
app.config['MAIL_DEFAULT_SENDER'] = 'admin@diakriszuluinvestmentsprojects.co.za'
mail = Mail(app)

# === Token Serializer ===
serializer = URLSafeTimedSerializer(app.secret_key)
# === OpenAI Setup ===
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === Environment Variables ===
DEPLOYMENT_MODE = os.getenv("SENTINEL_MODE", "on-premise")
connected_agents = {}

# === System Monitoring ===
system_metrics = {
    'cpu_usage': 0,
    'memory_usage': 0,
    'disk_usage': 0,
    'network_io': {'bytes_sent': 0, 'bytes_recv': 0},
    'active_connections': 0,
    'uptime': datetime.now(),
    'threats_detected': 0,
    'threats_blocked': 0
}

# === Database Migration Function ===
def migrate_database():
    """Handle database schema migrations"""
    db_path = 'users.db'
    
    try:
        # Check if database file exists
        if not os.path.exists(db_path):
            print("Database file doesn't exist, will be created fresh")
            return True
            
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if user table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user'")
        if not cursor.fetchone():
            print("User table doesn't exist, will be created fresh")
            conn.close()
            return True
        
        # Check if created_at column exists
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'created_at' not in columns:
            print("Adding missing created_at column to user table...")
            cursor.execute("ALTER TABLE user ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP")
            conn.commit()
            print("Successfully added created_at column")
        
        # Check if is_active column exists
        if 'is_active' not in columns:
            print("Adding missing is_active column to user table...")
            cursor.execute("ALTER TABLE user ADD COLUMN is_active BOOLEAN DEFAULT 1")
            conn.commit()
            print("Successfully added is_active column")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"Database migration error: {e}")
        print("Will attempt to recreate database with correct schema")
        try:
            conn.close()
        except:
            pass
        
        # Remove corrupted database file
        try:
            if os.path.exists(db_path):
                backup_name = f"{db_path}.backup_{int(time.time())}"
                os.rename(db_path, backup_name)
                print(f"Moved corrupted database to {backup_name}")
        except Exception as backup_error:
            print(f"Could not backup database: {backup_error}")
            
        return False

# === Models ===
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='viewer')
    features = db.Column(db.String(200), default="")
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

class ThreatLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    threat_type = db.Column(db.String(50), nullable=False)
    severity = db.Column(db.String(20), nullable=False)
    source_ip = db.Column(db.String(45))
    target_ip = db.Column(db.String(45))
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='detected')
    agent_id = db.Column(db.String(50))

class SystemEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    event_type = db.Column(db.String(50), nullable=False)
    module = db.Column(db.String(50))
    message = db.Column(db.Text)
    severity = db.Column(db.String(20), default='info')

# === Login Manager ===
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# === System Monitoring Functions ===
def update_system_metrics():
    """Update system metrics periodically"""
    while True:
        try:
            # CPU and Memory
            system_metrics['cpu_usage'] = psutil.cpu_percent(interval=1)
            system_metrics['memory_usage'] = psutil.virtual_memory().percent
            system_metrics['disk_usage'] = psutil.disk_usage('/').percent
            
            # Network I/O
            net_io = psutil.net_io_counters()
            system_metrics['network_io'] = {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv
            }
            
            # Active connections
            system_metrics['active_connections'] = len(connected_agents)
            
            # Create a JSON-serializable version of system_metrics for Socket.IO
            serializable_metrics = {
                'cpu_usage': system_metrics['cpu_usage'],
                'memory_usage': system_metrics['memory_usage'],
                'disk_usage': system_metrics['disk_usage'],
                'network_io': system_metrics['network_io'],
                'active_connections': system_metrics['active_connections'],
                'uptime': str(datetime.now() - system_metrics['uptime']).split('.')[0],
                'threats_detected': system_metrics['threats_detected'],
                'threats_blocked': system_metrics['threats_blocked']
            }
            
            # Emit to connected clients
            socketio.emit('system_update', serializable_metrics)
            
        except Exception as e:
            print(f"Error updating system metrics: {e}")
        
        time.sleep(5)  # Update every 5 seconds

# === Routes ===
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Please provide both email and password', 'error')
            return render_template('login.html')
        
        try:
            user = User.query.filter_by(email=email).first()
            
            if user and check_password_hash(user.password, password):
                login_user(user)
                user.last_seen = datetime.utcnow()
                db.session.commit()
                
                # Log login event
                event = SystemEvent(
                    event_type='user_login',
                    message=f'User {email} logged in successfully',
                    severity='info'
                )
                db.session.add(event)
                db.session.commit()
                
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password', 'error')
                
        except Exception as e:
            print(f"Login error: {e}")
            flash('Login system error. Please try again.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    try:
        # Log logout event
        event = SystemEvent(
            event_type='user_logout',
            message=f'User {current_user.email} logged out',
            severity='info'
        )
        db.session.add(event)
        db.session.commit()
    except Exception as e:
        print(f"Logout event logging error: {e}")
    
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        # Update user's last seen
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        
        # Get AMP Grid status
        grid_status = amp_grid.get_grid_status()
        
        # Get recent threats
        recent_threats = ThreatLog.query.order_by(ThreatLog.timestamp.desc()).limit(10).all()
        
        # Get system events
        recent_events = SystemEvent.query.order_by(SystemEvent.timestamp.desc()).limit(5).all()
        
        # Calculate uptime
        uptime = datetime.now() - system_metrics['uptime']
        
        dashboard_data = {
            'connected_agents': len(connected_agents),
            'user_count': User.query.count(),
            'current_user': current_user.email,
            'user_role': current_user.role,
            'deployment_mode': DEPLOYMENT_MODE,
            'amp_grid': grid_status,
            'recent_threats': [
                {
                    'timestamp': threat.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'type': threat.threat_type,
                    'severity': threat.severity,
                    'source_ip': threat.source_ip,
                    'status': threat.status
                } for threat in recent_threats
            ],
            'recent_events': [
                {
                    'timestamp': event.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'type': event.event_type,
                    'message': event.message,
                    'severity': event.severity
                } for event in recent_events
            ],
            'system_metrics': system_metrics,
            'uptime': str(uptime).split('.')[0],
            'threats_today': ThreatLog.query.filter(
                ThreatLog.timestamp >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            ).count()
        }
        
        return render_template('dashboard.html', data=dashboard_data, mode=DEPLOYMENT_MODE)
    
    except Exception as e:
        print(f"Dashboard error: {e}")
        flash(f'Error loading dashboard: {str(e)}', 'error')
        # Return minimal dashboard data to prevent complete failure
        minimal_data = {
            'connected_agents': 0,
            'user_count': 1,
            'current_user': current_user.email if current_user.is_authenticated else 'Unknown',
            'user_role': current_user.role if current_user.is_authenticated else 'viewer',
            'deployment_mode': DEPLOYMENT_MODE,
            'amp_grid': {'metrics': {'total_tasks': 0, 'completed_tasks': 0, 'failed_tasks': 0}},
            'recent_threats': [],
            'recent_events': [],
            'system_metrics': system_metrics,
            'uptime': '0:00:00',
            'threats_today': 0
        }
        return render_template('dashboard.html', data=minimal_data, mode=DEPLOYMENT_MODE)

# === AMP Grid Routes ===
@app.route('/amp_grid')
@login_required
def amp_grid_dashboard():
    """AMP Thread Grid dashboard"""
    try:
        grid_status = amp_grid.get_grid_status()
        return render_template('amp_grid.html', grid_data=grid_status)
    except Exception as e:
        flash(f'Error loading AMP Grid dashboard: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/api/amp/submit_task', methods=['POST'])
@login_required
def submit_amp_task():
    """Submit a task to the AMP grid"""
    try:
        data = request.get_json()
        task_type = data.get('task_type')
        payload = data.get('payload', {})
        priority = TaskPriority[data.get('priority', 'NORMAL')]
        
        task_id = amp_grid.submit_task(task_type, payload, priority)
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': 'Task submitted successfully'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/amp/task_status/<task_id>')
@login_required
def get_amp_task_status(task_id):
    """Get status of a specific task"""
    try:
        status = amp_grid.get_task_status(task_id)
        if status:
            return jsonify(status)
        else:
            return jsonify({'error': 'Task not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/amp/grid_status')
@login_required
def get_amp_grid_status():
    """Get current AMP grid status"""
    try:
        status = amp_grid.get_grid_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/amp/run_security_scan', methods=['POST'])
@login_required
def run_security_scan():
    """Run a comprehensive security scan using AMP grid"""
    try:
        # Submit multiple tasks for comprehensive scan
        tasks = []
        
        # Threat scanning
        threat_task = amp_grid.submit_task('threat_scan', {
            'scan_type': 'comprehensive',
            'scan_count': 500
        }, TaskPriority.HIGH)
        tasks.append(threat_task)
        
        # Vulnerability scanning
        vuln_task = amp_grid.submit_task('vulnerability_scan', {
            'target_count': 10
        }, TaskPriority.HIGH)
        tasks.append(vuln_task)
        
        # Network monitoring
        network_task = amp_grid.submit_task('network_monitoring', {
            'connection_count': 100
        }, TaskPriority.NORMAL)
        tasks.append(network_task)
        
        # Log processing
        log_task = amp_grid.submit_task('log_processing', {
            'log_count': 5000
        }, TaskPriority.NORMAL)
        tasks.append(log_task)
        
        # AI analysis
        ai_task = amp_grid.submit_task('ai_analysis', {
            'analysis_type': 'security_assessment'
        }, TaskPriority.HIGH)
        tasks.append(ai_task)
        
        return jsonify({
            'success': True,
            'message': 'Comprehensive security scan initiated',
            'task_ids': tasks
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# === Socket.IO Events ===
@socketio.on('connect')
@login_required
def handle_connect():
    """Handle client connection"""
    emit('connected', {'data': 'Connected to SentinelIT AMP Grid'})

@socketio.on('disconnect')
@login_required
def handle_disconnect():
    """Handle client disconnection"""
    print(f'Client disconnected: {current_user.email if current_user.is_authenticated else "Unknown"}')

# === Initialize Database ===
def init_db():
    """Initialize database with default admin user"""
    with app.app_context():
        # Run database migration first
        migration_success = migrate_database()
        
        # Create all tables (this will create fresh tables if database was recreated)
        try:
            db.create_all()
            print("✅ Database tables created successfully")
        except Exception as e:
            print(f"❌ Error creating database tables: {e}")
            return
        
        # Create default admin user if none exists
        try:
            existing_admin = User.query.filter_by(email='admin@sentinel.com').first()
            if not existing_admin:
                admin_user = User(
                    email='admin@sentinel.com',
                    password=generate_password_hash('admin123'),
                    role='admin',
                    created_at=datetime.utcnow(),
                    is_active=True
                )
                db.session.add(admin_user)
                db.session.commit()
                print("✅ Default admin user created: admin@sentinel.com / admin123")
            else:
                print("ℹ️  Admin user already exists")
                
        except Exception as e:
            print(f"❌ Error creating admin user: {e}")
            db.session.rollback()
            
            # If there's still an issue, recreate the database completely
            print("🔄 Attempting to recreate database completely...")
            try:
                # Drop all tables and recreate
                db.drop_all()
                db.create_all()
                
                # Create admin user again
                admin_user = User(
                    email='admin@sentinel.com',
                    password=generate_password_hash('admin123'),
                    role='admin',
                    created_at=datetime.utcnow(),
                    is_active=True
                )
                db.session.add(admin_user)
                db.session.commit()
                print("✅ Database recreated successfully with admin user")
                
            except Exception as recreate_error:
                print(f"❌ Failed to recreate database: {recreate_error}")
                print("Please delete the users.db file manually and restart the application")

# === Initialize AMP Grid ===
def init_amp_grid():
    """Initialize and configure the AMP Thread Grid"""
    global amp_grid
    
    try:
        # Initialize AMP Thread Grid with app context
        amp_grid = AMPThreadGrid(app)
        
        # Register task handlers
        amp_grid.register_task_handler('threat_scan', threat_scanner_handler)
        amp_grid.register_task_handler('packet_analysis', packet_analyzer_handler)
        amp_grid.register_task_handler('vulnerability_scan', vulnerability_scanner_handler)
        amp_grid.register_task_handler('log_processing', log_processor_handler)
        amp_grid.register_task_handler('ai_analysis', ai_analyzer_handler)
        amp_grid.register_task_handler('network_monitoring', network_monitor_handler)
        
        print("✅ AMP Thread Grid initialized and configured")
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize AMP Thread Grid: {e}")
        return False

# === Main ===
if __name__ == '__main__':
    print("🚀 SentinelIT Command Center Starting...")
    print("=" * 50)
    
    # Initialize database
    print("📊 Initializing database...")
    init_db()
    
    # Initialize AMP Grid
    print("⚙️  Initializing AMP Thread Grid...")
    if not init_amp_grid():
        print("❌ Failed to start AMP Grid, exiting...")
        exit(1)
    
    # Start AMP Thread Grid
    amp_grid.start_grid()
    
    # Start system monitoring
    print("📡 Starting system monitoring...")
    monitoring_thread = threading.Thread(target=update_system_metrics, daemon=True)
    monitoring_thread.start()
    
    # Print startup information
    print("\n" + "=" * 50)
    print("🎯 SentinelIT Command Center Ready!")
    print("=" * 50)
    print(f"🌐 Deployment Mode: {DEPLOYMENT_MODE}")
    print("🔧 AMP Grid Workers initialized:")
    for worker_id, worker in amp_grid.workers.items():
        print(f"   • {worker_id}: {worker.max_threads} threads ({worker.worker_type})")
    print(f"\n📱 Access Points:")
    print(f"   • Main Dashboard: http://localhost:5000")
    print(f"   • AMP Grid Dashboard: http://localhost:5000/amp_grid")
    print(f"   • Default Login: admin@sentinel.com / admin123")
    print("=" * 50)
    
    # Start Flask-SocketIO server
    try:
        socketio.run(app, debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        # Gracefully shutdown AMP Grid
        if 'amp_grid' in globals():
            amp_grid.stop_grid()        
