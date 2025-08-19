# data_collector.py - SentinelIT Real-Time Data Collection System
import psutil
import sqlite3
import json
import time
import threading
import socket
import subprocess
import platform
import requests
from datetime import datetime, timedelta
import logging
import os
import hashlib
import winreg if platform.system() == "Windows" else None

class SentinelITDataCollector:
    def __init__(self):
        self.db_path = "sentinelit_data.db"
        self.collection_interval = 5  # seconds
        self.is_running = False
        
        self.setup_logging()
        self.setup_database()
        
        print("🛡️  SentinelIT Data Collector Initialized")
        print("📊 Real-time system monitoring active")
        
    def setup_logging(self):
        """Setup logging for data collector"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - DataCollector - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('sentinelit_datacollector.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('SentinelIT-DataCollector')
        
    def setup_database(self):
        """Create database tables for collected data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # System metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                cpu_percent REAL,
                memory_percent REAL,
                disk_percent REAL,
                network_bytes_sent INTEGER,
                network_bytes_received INTEGER,
                active_processes INTEGER,
                system_load_1m REAL,
                system_load_5m REAL,
                system_load_15m REAL
            )
        ''')
        
        # Network connections table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS network_connections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                local_address TEXT,
                local_port INTEGER,
                remote_address TEXT,
                remote_port INTEGER,
                status TEXT,
                process_id INTEGER,
                process_name TEXT
            )
        ''')
        
        # Security events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                event_type TEXT,
                severity TEXT,
                source TEXT,
                description TEXT,
                additional_data TEXT
            )
        ''')
        
        # Process monitoring table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS process_monitor (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                process_id INTEGER,
                process_name TEXT,
                cpu_percent REAL,
                memory_percent REAL,
                status TEXT,
                command_line TEXT,
                parent_pid INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
        self.logger.info("Database initialized successfully")
        
    def collect_system_metrics(self):
        """Collect real-time system performance metrics"""
        try:
            # CPU and Memory metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network metrics
            network = psutil.net_io_counters()
            
            # Process count
            active_processes = len(psutil.pids())
            
            # System load (Unix systems)
            try:
                load_1m, load_5m, load_15m = os.getloadavg()
            except:
                load_1m = load_5m = load_15m = 0.0
            
            # Store in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO system_metrics 
                (cpu_percent, memory_percent, disk_percent, network_bytes_sent, 
                 network_bytes_received, active_processes, system_load_1m, 
                 system_load_5m, system_load_15m)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                cpu_percent, memory.percent, disk.percent,
                network.bytes_sent, network.bytes_recv, active_processes,
                load_1m, load_5m, load_15m
            ))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"System metrics collected - CPU: {cpu_percent:.1f}%, RAM: {memory.percent:.1f}%")
            
            # Check for anomalies
            self.check_system_anomalies(cpu_percent, memory.percent, disk.percent)
            
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {str(e)}")
    
    def collect_network_connections(self):
        """Monitor active network connections"""
        try:
            connections = psutil.net_connections(kind='inet')
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Clear old connections (keep only last hour)
            cursor.execute('''
                DELETE FROM network_connections 
                WHERE timestamp < datetime('now', '-1 hour')
            ''')
            
            for connection in connections:
                if connection.raddr:  # Only monitor established connections
                    try:
                        process = psutil.Process(connection.pid) if connection.pid else None
                        process_name = process.name() if process else "Unknown"
                        
                        cursor.execute('''
                            INSERT INTO network_connections 
                            (local_address, local_port, remote_address, remote_port, 
                             status, process_id, process_name)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            connection.laddr.ip, connection.laddr.port,
                            connection.raddr.ip, connection.raddr.port,
                            connection.status, connection.pid, process_name
                        ))
                        
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Network connections collected: {len(connections)} active")
            
        except Exception as e:
            self.logger.error(f"Error collecting network connections: {str(e)}")
    
    def collect_process_data(self):
        """Monitor running processes for security analysis"""
        try:
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status', 'cmdline', 'ppid']):
                try:
                    pinfo = proc.info
                    processes.append(pinfo)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Clear old process data
            cursor.execute('''
                DELETE FROM process_monitor 
                WHERE timestamp < datetime('now', '-2 hours')
            ''')
            
            # Store current processes
            for proc in processes:
                cursor.execute('''
                    INSERT INTO process_monitor 
                    (process_id, process_name, cpu_percent, memory_percent, 
                     status, command_line, parent_pid)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    proc['pid'], proc['name'], proc['cpu_percent'] or 0,
                    proc['memory_percent'] or 0, proc['status'],
                    ' '.join(proc['cmdline'] or [])[:500],  # Limit cmdline length
                    proc['ppid']
                ))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Process data collected: {len(processes)} processes")
            
            # Check for suspicious processes
            self.check_suspicious_processes(processes)
            
        except Exception as e:
            self.logger.error(f"Error collecting process data: {str(e)}")
    
    def check_system_anomalies(self, cpu, memory, disk):
        """Check for system performance anomalies"""
        try:
            anomalies = []
            
            if cpu > 90:
                anomalies.append(f"High CPU usage: {cpu:.1f}%")
            
            if memory > 85:
                anomalies.append(f"High memory usage: {memory:.1f}%")
                
            if disk > 90:
                anomalies.append(f"High disk usage: {disk:.1f}%")
            
            if anomalies:
                self.log_security_event(
                    "SYSTEM_ANOMALY", "HIGH", "DataCollector",
                    f"Performance anomalies detected: {', '.join(anomalies)}"
                )
                
        except Exception as e:
            self.logger.error(f"Error checking system anomalies: {str(e)}")
    
    def check_suspicious_processes(self, processes):
        """Check for potentially suspicious processes"""
        try:
            suspicious_names = [
                'nc', 'netcat', 'ncat', 'socat',  # Network tools
                'psexec', 'wmic', 'powershell',    # Administrative tools
                'mimikatz', 'procdump',            # Security tools
                'tor', 'proxychains',              # Anonymization tools
            ]
            
            suspicious_found = []
            
            for proc in processes:
                proc_name = proc['name'].lower()
                cmdline = ' '.join(proc['cmdline'] or []).lower()
                
                # Check suspicious process names
                for sus_name in suspicious_names:
                    if sus_name in proc_name or sus_name in cmdline:
                        suspicious_found.append(f"{proc['name']} (PID: {proc['pid']})")
                
                # Check for high resource usage
                if proc['cpu_percent'] and proc['cpu_percent'] > 80:
                    suspicious_found.append(f"High CPU process: {proc['name']} ({proc['cpu_percent']:.1f}%)")
            
            if suspicious_found:
                self.log_security_event(
                    "SUSPICIOUS_PROCESS", "MEDIUM", "DataCollector",
                    f"Suspicious processes detected: {', '.join(suspicious_found[:5])}"  # Limit to first 5
                )
                
        except Exception as e:
            self.logger.error(f"Error checking suspicious processes: {str(e)}")
    
    def collect_file_integrity_data(self):
        """Monitor critical system files for integrity"""
        try:
            critical_files = [
                '/etc/passwd', '/etc/shadow', '/etc/hosts',  # Linux
                'C:\\Windows\\System32\\drivers\\etc\\hosts',  # Windows
                'C:\\Windows\\System32\\config\\SAM',          # Windows
            ]
            
            file_hashes = {}
            
            for file_path in critical_files:
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'rb') as f:
                            file_hash = hashlib.sha256(f.read()).hexdigest()
                            file_hashes[file_path] = file_hash
                    except (PermissionError, OSError):
                        continue
            
            # Store file integrity data
            if file_hashes:
                self.log_security_event(
                    "FILE_INTEGRITY_CHECK", "INFO", "DataCollector",
                    f"File integrity check completed for {len(file_hashes)} files",
                    json.dumps(file_hashes)
                )
                
        except Exception as e:
            self.logger.error(f"Error collecting file integrity data: {str(e)}")
    
    def log_security_event(self, event_type, severity, source, description, additional_data=""):
        """Log security events to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO security_events 
                (event_type, severity, source, description, additional_data)
                VALUES (?, ?, ?, ?, ?)
            ''', (event_type, severity, source, description, additional_data))
            
            conn.commit()
            conn.close()
            
            self.logger.warning(f"Security event logged: {event_type} - {description}")
            
        except Exception as e:
            self.logger.error(f"Error logging security event: {str(e)}")
    
    def get_system_overview(self):
        """Get current system overview"""
        try:
            # Get latest system metrics
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM system_metrics 
                ORDER BY timestamp DESC 
                LIMIT 1
            ''')
            
            latest_metrics = cursor.fetchone()
            
            # Get recent security events
            cursor.execute('''
                SELECT COUNT(*) FROM security_events 
                WHERE timestamp > datetime('now', '-1 hour')
            ''')
            
            recent_events = cursor.fetchone()[0]
            
            # Get active connections count
            cursor.execute('''
                SELECT COUNT(*) FROM network_connections 
                WHERE timestamp > datetime('now', '-5 minutes')
            ''')
            
            active_connections = cursor.fetchone()[0]
            
            conn.close()
            
            overview = {
                'system_metrics': latest_metrics,
                'recent_security_events': recent_events,
                'active_connections': active_connections,
                'data_collector_status': 'running' if self.is_running else 'stopped'
            }
            
            return overview
            
        except Exception as e:
            self.logger.error(f"Error getting system overview: {str(e)}")
            return {}
    
    def start_collection(self):
        """Start continuous data collection"""
        self.is_running = True
        self.logger.info("🚀 Starting SentinelIT Data Collection...")
        
        def collection_loop():
            while self.is_running:
                try:
                    # Collect different types of data
                    self.collect_system_metrics()
                    time.sleep(2)
                    
                    self.collect_network_connections()
                    time.sleep(2)
                    
                    self.collect_process_data()
                    time.sleep(2)
                    
                    # File integrity check every 10 minutes
                    if int(time.time()) % 600 == 0:
                        self.collect_file_integrity_data()
                    
                    # Wait for next collection cycle
                    time.sleep(self.collection_interval)
                    
                except KeyboardInterrupt:
                    self.logger.info("Data collection interrupted by user")
                    break
                except Exception as e:
                    self.logger.error(f"Error in collection loop: {str(e)}")
                    time.sleep(10)  # Wait longer on error
        
        # Start collection in separate thread
        collection_thread = threading.Thread(target=collection_loop)
        collection_thread.daemon = True
        collection_thread.start()
        
        self.logger.info("✅ Data collection started successfully")
        return collection_thread
    
    def stop_collection(self):
        """Stop data collection"""
        self.is_running = False
        self.logger.info("🛑 Data collection stopped")

def main():
    """Main function to run data collector"""
    collector = SentinelITDataCollector()
    
    print("\n" + "="*60)
    print("🛡️  SENTINELIT DATA COLLECTOR")
    print("="*60)
    print("📊 Real-time system monitoring")
    print("🔍 Network connection tracking")
    print("⚠️  Security anomaly detection")
    print("📁 File integrity monitoring")
    print("="*60 + "\n")
    
    try:
        # Start data collection
        collection_thread = collector.start_collection()
        
        print("📈 Data Collection Status:")
        print("  ✅ System Metrics")
        print("  ✅ Network Monitoring")
        print("  ✅ Process Tracking")
        print("  ✅ Security Events")
        print("\n🎮 Press Ctrl+C to stop\n")
        
        # Keep main thread alive
        while collector.is_running:
            time.sleep(10)
            
            # Print periodic status
            overview = collector.get_system_overview()
            if overview and overview.get('system_metrics'):
                metrics = overview['system_metrics']
                print(f"💻 System Status - CPU: {metrics[2]:.1f}% | RAM: {metrics[3]:.1f}% | Events: {overview['recent_security_events']}")
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Data Collector...")
        collector.stop_collection()
        print("✅ Data Collector stopped successfully")

if __name__ == "__main__":
    main()