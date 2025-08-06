from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
import os
import time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # ✅ This loads environment variables from your .env file

import time
import psutil
from datetime import datetime, timedelta
import threading
import json
import queue
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import asyncio
import hashlib
import uuid
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from enum import Enum
import sqlite3

# === AMP Thread Grid System ===
class TaskPriority(Enum):
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class AMPTask:
    task_id: str
    task_type: str
    priority: TaskPriority
    payload: Dict[str, Any]
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    worker_id: Optional[str] = None
    thread_id: Optional[str] = None

class AMPWorker:
    def __init__(self, worker_id: str, worker_type: str, max_threads: int = 4):
        self.worker_id = worker_id
        self.worker_type = worker_type
        self.max_threads = max_threads
        self.is_active = True
        self.current_tasks = {}
        self.completed_tasks = 0
        self.failed_tasks = 0
        self.last_heartbeat = datetime.now()
        self.executor = ThreadPoolExecutor(max_workers=max_threads)
        
    def get_status(self):
        return {
            'worker_id': self.worker_id,
            'worker_type': self.worker_type,
            'active_threads': len(self.current_tasks),
            'max_threads': self.max_threads,
            'completed_tasks': self.completed_tasks,
            'failed_tasks': self.failed_tasks,
            'is_active': self.is_active,
            'last_heartbeat': self.last_heartbeat.isoformat(),
            'current_tasks': list(self.current_tasks.keys())
        }

class AMPThreadGrid:
    def __init__(self, app=None):
        self.app = app
        self.workers: Dict[str, AMPWorker] = {}
        self.task_queue = queue.PriorityQueue()
        self.task_registry: Dict[str, AMPTask] = {}
        self.task_handlers = {}
        self.is_running = False
        self.grid_lock = threading.Lock()
        self.metrics = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'active_workers': 0,
            'grid_uptime': datetime.now()
        }
        
        # Initialize default workers
        self._initialize_workers()
        
    def _initialize_workers(self):
        """Initialize default worker pool"""
        worker_configs = [
            {'type': 'threat_scanner', 'count': 2, 'threads': 4},
            {'type': 'packet_analyzer', 'count': 2, 'threads': 6},
            {'type': 'vulnerability_scanner', 'count': 1, 'threads': 8},
            {'type': 'log_processor', 'count': 2, 'threads': 3},
            {'type': 'ai_analyzer', 'count': 1, 'threads': 2},
            {'type': 'network_monitor', 'count': 3, 'threads': 4}
        ]
        
        for config in worker_configs:
            for i in range(config['count']):
                worker_id = f"{config['type']}_{i+1}"
                self.workers[worker_id] = AMPWorker(
                    worker_id=worker_id,
                    worker_type=config['type'],
                    max_threads=config['threads']
                )
    
    def register_task_handler(self, task_type: str, handler_func):
        """Register a task handler function"""
        self.task_handlers[task_type] = handler_func
    
    def submit_task(self, task_type: str, payload: Dict[str, Any], 
                   priority: TaskPriority = TaskPriority.NORMAL) -> str:
        """Submit a new task to the grid"""
        task_id = str(uuid.uuid4())
        task = AMPTask(
            task_id=task_id,
            task_type=task_type,
            priority=priority,
            payload=payload,
            created_at=datetime.now()
        )
        
        self.task_registry[task_id] = task
        self.task_queue.put((priority.value, task_id))
        self.metrics['total_tasks'] += 1
        
        if self.app:
            with self.app.app_context():
                socketio.emit('task_submitted', {
                    'task_id': task_id,
                    'task_type': task_type,
                    'priority': priority.name
                })
        
        return task_id
    
    def get_available_worker(self, task_type: str) -> Optional[AMPWorker]:
        """Find an available worker for the task type"""
        available_workers = [
            worker for worker in self.workers.values()
            if (worker.worker_type == task_type or task_type == 'general') 
            and len(worker.current_tasks) < worker.max_threads
            and worker.is_active
        ]
        
        if available_workers:
            # Return worker with least current tasks
            return min(available_workers, key=lambda w: len(w.current_tasks))
        return None
    
    def execute_task(self, task: AMPTask, worker: AMPWorker):
        """Execute a task on a specific worker"""
        def task_wrapper():
            thread_id = threading.current_thread().ident
            task.started_at = datetime.now()
            task.status = TaskStatus.RUNNING
            task.worker_id = worker.worker_id
            task.thread_id = str(thread_id)
            
            worker.current_tasks[task.task_id] = task
            
            try:
                if task.task_type in self.task_handlers:
                    result = self.task_handlers[task.task_type](task.payload)
                    task.result = result
                    task.status = TaskStatus.COMPLETED
                    worker.completed_tasks += 1
                    self.metrics['completed_tasks'] += 1
                else:
                    raise Exception(f"No handler for task type: {task.task_type}")
                    
            except Exception as e:
                task.error = str(e)
                task.status = TaskStatus.FAILED
                worker.failed_tasks += 1
                self.metrics['failed_tasks'] += 1
            
            finally:
                task.completed_at = datetime.now()
                worker.current_tasks.pop(task.task_id, None)
                
                if self.app:
                    with self.app.app_context():
                        socketio.emit('task_completed', {
                            'task_id': task.task_id,
                            'status': task.status.value,
                            'worker_id': worker.worker_id,
                            'duration': (task.completed_at - task.started_at).total_seconds()
                        })
        
        worker.executor.submit(task_wrapper)
    
    def start_grid(self):
        """Start the AMP thread grid"""
        self.is_running = True
        threading.Thread(target=self._grid_scheduler, daemon=True).start()
        threading.Thread(target=self._heartbeat_monitor, daemon=True).start()
        print("AMP Thread Grid started successfully")
    
    def _grid_scheduler(self):
        """Main grid scheduler loop"""
        while self.is_running:
            try:
                if not self.task_queue.empty():
                    priority, task_id = self.task_queue.get(timeout=1)
                    task = self.task_registry.get(task_id)
                    
                    if task and task.status == TaskStatus.PENDING:
                        worker = self.get_available_worker(task.task_type)
                        if worker:
                            self.execute_task(task, worker)
                        else:
                            # No available worker, put back in queue
                            self.task_queue.put((priority, task_id))
                            time.sleep(0.1)
                else:
                    time.sleep(0.1)
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Grid scheduler error: {e}")
    
    def _heartbeat_monitor(self):
        """Monitor worker heartbeats and grid health"""
        while self.is_running:
            current_time = datetime.now()
            
            for worker in self.workers.values():
                worker.last_heartbeat = current_time
                
            self.metrics['active_workers'] = len([w for w in self.workers.values() if w.is_active])
            
            # Emit grid status
            if self.app:
                with self.app.app_context():
                    socketio.emit('grid_status', self.get_grid_status())
            
            time.sleep(5)
    
    def get_grid_status(self):
        """Get current grid status"""
        return {
            'metrics': self.metrics,
            'workers': {worker_id: worker.get_status() for worker_id, worker in self.workers.items()},
            'queue_size': self.task_queue.qsize(),
            'active_tasks': len([task for task in self.task_registry.values() 
                               if task.status == TaskStatus.RUNNING])
        }
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get status of a specific task"""
        task = self.task_registry.get(task_id)
        if task:
            return {
                'task_id': task.task_id,
                'task_type': task.task_type,
                'status': task.status.value,
                'priority': task.priority.name,
                'created_at': task.created_at.isoformat(),
                'started_at': task.started_at.isoformat() if task.started_at else None,
                'completed_at': task.completed_at.isoformat() if task.completed_at else None,
                'worker_id': task.worker_id,
                'thread_id': task.thread_id,
                'result': task.result,
                'error': task.error
            }
        return None

# === Task Handlers ===
def threat_scanner_handler(payload):
    """Handle threat scanning tasks"""
    time.sleep(2)  # Simulate scanning time
    return {
        'threats_found': payload.get('scan_count', 0),
        'scan_type': payload.get('scan_type', 'full'),
        'status': 'completed'
    }

def packet_analyzer_handler(payload):
    """Handle packet analysis tasks"""
    time.sleep(1.5)  # Simulate analysis time
    return {
        'packets_analyzed': payload.get('packet_count', 100),
        'suspicious_packets': payload.get('packet_count', 100) // 10,
        'analysis_complete': True
    }

def vulnerability_scanner_handler(payload):
    """Handle vulnerability scanning tasks"""
    time.sleep(3)  # Simulate vulnerability scan
    return {
        'vulnerabilities_found': payload.get('target_count', 1) * 2,
        'severity_high': 1,
        'severity_medium': 3,
        'severity_low': 2
    }

def log_processor_handler(payload):
    """Handle log processing tasks"""
    time.sleep(0.5)  # Simulate log processing
    return {
        'logs_processed': payload.get('log_count', 1000),
        'alerts_generated': payload.get('log_count', 1000) // 100,
        'processing_time': 0.5
    }

def ai_analyzer_handler(payload):
    """Handle AI analysis tasks"""
    time.sleep(4)  # Simulate AI processing
    return {
        'analysis_type': payload.get('analysis_type', 'behavior'),
        'confidence_score': 0.87,
        'recommendation': 'Monitor closely',
        'ai_model_used': 'SentinelAI-v2'
    }

def network_monitor_handler(payload):
    """Handle network monitoring tasks"""
    time.sleep(1)  # Simulate network monitoring
    return {
        'connections_monitored': payload.get('connection_count', 50),
        'anomalies_detected': payload.get('connection_count', 50) // 20,
        'bandwidth_usage': '75%'
    }

# === Flask App Setup ===
app = Flask(__name__)
app.secret_key = 'sentinel-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Initialize AMP Thread Grid
amp_grid = AMPThreadGrid(app)

# Register task handlers
amp_grid.register_task_handler('threat_scan', threat_scanner_handler)
amp_grid.register_task_handler('packet_analysis', packet_analyzer_handler)
amp_grid.register_task_handler('vulnerability_scan', vulnerability_scanner_handler)
amp_grid.register_task_handler('log_processing', log_processor_handler)
amp_grid.register_task_handler('ai_analysis', ai_analyzer_handler)
amp_grid.register_task_handler('network_monitoring', network_monitor_handler)

# === Mail Config ===
app.config['MAIL_SERVER'] = 'mail.diakriszuluinvestmentsprojects.co.za'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'admin@diakriszuluinvestmentsprojects.co.za'
app.config['MAIL_PASSWORD'] = '0E6TkRTZms'
app.config['MAIL_DEFAULT_SENDER'] = 'admin@diakriszuluinvestmentsprojects.co.za'
mail = Mail(app)

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
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
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
        
    except Exception as e:
        print(f"Database migration error: {e}")
        # If migration fails, we might need to recreate the database
        print("Migration failed, consider backing up data and recreating database")

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
    return User.query.get(int(user_id))

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
            
            # Emit to connected clients
            socketio.emit('system_update', system_metrics)
            
        except Exception as e:
            print(f"Error updating system metrics: {e}")
        
        time.sleep(5)  # Update every 5 seconds

# Start monitoring thread
monitoring_thread = threading.Thread(target=update_system_metrics, daemon=True)
monitoring_thread.start()

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
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    # Log logout event
    event = SystemEvent(
        event_type='user_logout',
        message=f'User {current_user.email} logged out',
        severity='info'
    )
    db.session.add(event)
    db.session.commit()
    
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
            'uptime': str(uptime).split('.')[0],  # Remove microseconds
            'threats_today': ThreatLog.query.filter(
                ThreatLog.timestamp >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            ).count()
        }
        
        return render_template('dashboard.html', data=dashboard_data, mode=DEPLOYMENT_MODE)
    
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return render_template('dashboard.html', data={}, mode=DEPLOYMENT_MODE)

# === AMP Grid Routes ===
@app.route('/amp_grid')
@login_required
def amp_grid_dashboard():
    """AMP Thread Grid dashboard"""
    grid_status = amp_grid.get_grid_status()
    return render_template('amp_grid.html', grid_data=grid_status)

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
    print(f'Client disconnected: {current_user.email}')

# === Initialize Database ===
def init_db():
    """Initialize database with default admin user"""
    with app.app_context():
        # Run database migration first
        migrate_database()
        
        # Create all tables
        db.create_all()
        
        # Create default admin user if none exists
        try:
            if not User.query.filter_by(email='admin@sentinel.com').first():
                admin_user = User(
                    email='admin@sentinel.com',
                    password=generate_password_hash('admin123'),
                    role='admin',
                    created_at=datetime.utcnow(),
                    is_active=True
                )
                db.session.add(admin_user)
                db.session.commit()
                print("Default admin user created: admin@sentinel.com / admin123")
        except Exception as e:
            print(f"Error creating admin user: {e}")
            db.session.rollback()

# === Main ===
if __name__ == '__main__':
    init_db()
    
    # Start AMP Thread Grid
    amp_grid.start_grid()
    
    print("SentinelIT Command Center with AMP Thread Grid starting...")
    print(f"Deployment Mode: {DEPLOYMENT_MODE}")
    print("AMP Grid Workers initialized:")
    for worker_id, worker in amp_grid.workers.items():
        print(f"  - {worker_id}: {worker.max_threads} threads ({worker.worker_type})")
    print("Access the dashboard at: http://localhost:5000")
    print("Access AMP Grid dashboard at: http://localhost:5000/amp_grid")
    print("Default login: admin@sentinel.com / admin123")
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)