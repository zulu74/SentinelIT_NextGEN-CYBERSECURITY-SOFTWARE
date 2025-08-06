# amp_grid.py - Separate AMP Thread Grid Module

import threading
import queue
import time
import uuid
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from enum import Enum
import json

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
    def __init__(self, app=None, socketio=None):
        self.app = app
        self.socketio = socketio
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
        
        if self.socketio:
            self.socketio.emit('task_submitted', {
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
            return min(available_workers, key=lambda w: len(w.current_tasks))
        return None
    
    def start_grid(self):
        """Start the AMP thread grid"""
        self.is_running = True
        threading.Thread(target=self._grid_scheduler, daemon=True).start()
        threading.Thread(target=self._heartbeat_monitor, daemon=True).start()
        print("🚀 AMP Thread Grid started successfully")
    
    def stop_grid(self):
        """Stop the AMP thread grid"""
        self.is_running = False
        print("⏹️ AMP Thread Grid stopped")
    
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
                            self.task_queue.put((priority, task_id))
                            time.sleep(0.1)
                else:
                    time.sleep(0.1)
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Grid scheduler error: {e}")
    
    def _heartbeat_monitor(self):
        """Monitor worker heartbeats and grid health"""
        while self.is_running:
            current_time = datetime.now()
            
            for worker in self.workers.values():
                worker.last_heartbeat = current_time
                
            self.metrics['active_workers'] = len([w for w in self.workers.values() if w.is_active])
            
            # Emit grid status (only if socketio is available)
            if self.socketio:
                self.socketio.emit('grid_status', self.get_grid_status())
            
            time.sleep(5)
    
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
                    print(f"✅ Task {task.task_id[:8]} completed by {worker.worker_id}")
                else:
                    raise Exception(f"No handler for task type: {task.task_type}")
                    
            except Exception as e:
                task.error = str(e)
                task.status = TaskStatus.FAILED
                worker.failed_tasks += 1
                self.metrics['failed_tasks'] += 1
                print(f"❌ Task {task.task_id[:8]} failed: {e}")
            
            finally:
                task.completed_at = datetime.now()
                worker.current_tasks.pop(task.task_id, None)
                
                if self.socketio:
                    self.socketio.emit('task_completed', {
                        'task_id': task.task_id,
                        'status': task.status.value,
                        'worker_id': worker.worker_id,
                        'duration': (task.completed_at - task.started_at).total_seconds()
                    })
        
        worker.executor.submit(task_wrapper)
    
    def print_status(self):
        """Print current grid status to console"""
        status = self.get_grid_status()
        print("\n" + "="*60)
        print("🔹 AMP THREAD GRID STATUS")
        print("="*60)
        print(f"📊 Total Tasks: {status['metrics']['total_tasks']}")
        print(f"✅ Completed: {status['metrics']['completed_tasks']}")
        print(f"❌ Failed: {status['metrics']['failed_tasks']}")
        print(f"⚙️  Active Workers: {status['metrics']['active_workers']}")
        print(f"📋 Queue Size: {status['queue_size']}")
        print(f"🏃 Active Tasks: {status['active_tasks']}")
        print("\n🔧 WORKERS:")
        for worker_id, worker_info in status['workers'].items():
            print(f"  {worker_id}: {worker_info['active_threads']}/{worker_info['max_threads']} threads, "
                  f"✅{worker_info['completed_tasks']} ❌{worker_info['failed_tasks']}")
        print("="*60)

# Task handlers for various security operations
def threat_scanner_handler(payload):
    """Handle threat scanning tasks"""
    print(f"🔍 Running threat scan: {payload.get('scan_type', 'standard')}")
    time.sleep(2)  # Simulate scanning time
    return {
        'threats_found': payload.get('scan_count', 0) // 10,
        'scan_type': payload.get('scan_type', 'full'),
        'status': 'completed',
        'scan_duration': 2.0
    }

def packet_analyzer_handler(payload):
    """Handle packet analysis tasks"""
    print(f"📊 Analyzing {payload.get('packet_count', 100)} packets")
    time.sleep(1.5)  # Simulate analysis time
    return {
        'packets_analyzed': payload.get('packet_count', 100),
        'suspicious_packets': payload.get('packet_count', 100) // 10,
        'analysis_complete': True
    }

def vulnerability_scanner_handler(payload):
    """Handle vulnerability scanning tasks"""
    print(f"🛡️ Scanning {payload.get('target_count', 1)} targets for vulnerabilities")
    time.sleep(3)  # Simulate vulnerability scan
    return {
        'vulnerabilities_found': payload.get('target_count', 1) * 2,
        'severity_high': 1,
        'severity_medium': 3,
        'severity_low': 2
    }

def log_processor_handler(payload):
    """Handle log processing tasks"""
    print(f"📝 Processing {payload.get('log_count', 1000)} log entries")
    time.sleep(0.5)  # Simulate log processing
    return {
        'logs_processed': payload.get('log_count', 1000),
        'alerts_generated': payload.get('log_count', 1000) // 100,
        'processing_time': 0.5
    }

def ai_analyzer_handler(payload):
    """Handle AI analysis tasks"""
    print(f"🤖 Running AI analysis: {payload.get('analysis_type', 'behavior')}")
    time.sleep(4)  # Simulate AI processing
    return {
        'analysis_type': payload.get('analysis_type', 'behavior'),
        'confidence_score': 0.87,
        'recommendation': 'Monitor closely',
        'ai_model_used': 'SentinelAI-v2'
    }

def network_monitor_handler(payload):
    """Handle network monitoring tasks"""
    print(f"🌐 Monitoring {payload.get('connection_count', 50)} network connections")
    time.sleep(1)  # Simulate network monitoring
    return {
        'connections_monitored': payload.get('connection_count', 50),
        'anomalies_detected': payload.get('connection_count', 50) // 20,
        'bandwidth_usage': '75%'
    }

def run_demo():
    """Run a demonstration of the AMP Thread Grid"""
    print("🚀 Starting AMP Thread Grid Demo")
    print("="*50)
    
    # Create and configure the grid
    grid = AMPThreadGrid()
    
    # Register task handlers
    grid.register_task_handler('threat_scan', threat_scanner_handler)
    grid.register_task_handler('packet_analysis', packet_analyzer_handler)
    grid.register_task_handler('vulnerability_scan', vulnerability_scanner_handler)
    grid.register_task_handler('log_processing', log_processor_handler)
    grid.register_task_handler('ai_analysis', ai_analyzer_handler)
    grid.register_task_handler('network_monitoring', network_monitor_handler)
    
    # Start the grid
    grid.start_grid()
    
    # Submit various tasks
    tasks = []
    
    print("\n📤 Submitting tasks to the grid...")
    
    # Submit different types of tasks
    tasks.append(grid.submit_task('threat_scan', {
        'scan_type': 'comprehensive',
        'scan_count': 500
    }, TaskPriority.HIGH))
    
    tasks.append(grid.submit_task('packet_analysis', {
        'packet_count': 1000
    }, TaskPriority.NORMAL))
    
    tasks.append(grid.submit_task('vulnerability_scan', {
        'target_count': 5
    }, TaskPriority.HIGH))
    
    tasks.append(grid.submit_task('log_processing', {
        'log_count': 2000
    }, TaskPriority.LOW))
    
    tasks.append(grid.submit_task('ai_analysis', {
        'analysis_type': 'behavioral_anomaly'
    }, TaskPriority.CRITICAL))
    
    tasks.append(grid.submit_task('network_monitoring', {
        'connection_count': 100
    }, TaskPriority.NORMAL))
    
    print(f"✅ Submitted {len(tasks)} tasks to the grid")
    
    # Monitor progress
    print("\n⏳ Monitoring task execution...")
    completed_tasks = 0
    
    while completed_tasks < len(tasks):
        time.sleep(2)
        
        # Check task statuses
        completed_count = 0
        for task_id in tasks:
            status = grid.get_task_status(task_id)
            if status and status['status'] in ['completed', 'failed']:
                completed_count += 1
        
        if completed_count > completed_tasks:
            completed_tasks = completed_count
            grid.print_status()
    
    print("\n🎉 All tasks completed!")
    
    # Final status
    grid.print_status()
    
    # Show individual task results
    print("\n📋 TASK RESULTS:")
    print("-" * 50)
    for i, task_id in enumerate(tasks, 1):
        status = grid.get_task_status(task_id)
        if status:
            duration = 0
            if status['started_at'] and status['completed_at']:
                start = datetime.fromisoformat(status['started_at'])
                end = datetime.fromisoformat(status['completed_at'])
                duration = (end - start).total_seconds()
            
            print(f"{i}. {status['task_type']} - {status['status'].upper()}")
            print(f"   Worker: {status['worker_id']}")
            print(f"   Duration: {duration:.2f}s")
            if status['result']:
                print(f"   Result: {json.dumps(status['result'], indent=6)}")
            if status['error']:
                print(f"   Error: {status['error']}")
            print()
    
    # Stop the grid
    grid.stop_grid()
    print("🏁 Demo completed!")

if __name__ == "__main__":
    """Run the AMP Grid demo when executed directly"""
    run_demo()