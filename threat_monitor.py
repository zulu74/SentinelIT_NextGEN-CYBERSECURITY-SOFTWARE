import sqlite3
import time
import threading
import json
import requests
import hashlib
import socket
import subprocess
import psutil
import logging
import re
from datetime import datetime, timedelta
from collections import defaultdict, deque
import ipaddress

class SentinelITThreatMonitor:
    """
    A comprehensive real-time threat monitoring system for host-level security.
    It analyzes system metrics, network connections, and process behavior to detect
    anomalies and matches against known threat indicators.
    """
    def __init__(self):
        """Initializes the threat monitor with database connections and thresholds."""
        self.db_path = "sentinelit_threats.db"
        self.data_db_path = "sentinelit_data.db"
        self.monitoring_active = False
        
        # Threat detection thresholds
        self.thresholds = {
            'cpu_anomaly': 85.0,
            'memory_anomaly': 90.0,
            'network_anomaly': 100,  # connections per minute
            'failed_login_threshold': 5,
            'suspicious_port_threshold': 10
        }
        
        # Known threat indicators
        self.threat_patterns = {
            'suspicious_processes': [
                'nc', 'netcat', 'ncat', 'socat', 'telnet',
                'mimikatz', 'procdump', 'psexec', 'wmic',
                'tor', 'proxychains', 'nmap', 'masscan'
            ],
            'suspicious_commands': [
                'whoami', 'net user', 'net group', 'net localgroup',
                'tasklist', 'systeminfo', 'ipconfig', 'netstat',
                'reg query', 'powershell -enc', 'cmd /c'
            ],
            'malicious_ips': set(),  # Will be populated from threat feeds
            'suspicious_domains': set()
        }
        
        self.alert_history = deque(maxlen=1000)
        self.connection_baseline = defaultdict(int)
        
        self.setup_logging()
        self.setup_database()
        self.load_threat_intelligence() # Ensure intel is loaded on startup
        
        print("🛡️  SentinelIT Threat Monitor Initialized")
        print("👁️  Real-time threat detection active")
        
    def setup_logging(self):
        """Setup logging for threat monitor"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - ThreatMonitor - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('sentinelit_threatmonitor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('SentinelIT-ThreatMonitor')
    
    def setup_database(self):
        """Initialize threat monitoring database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Threat alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS threat_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                threat_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                source_ip TEXT,
                target_ip TEXT,
                process_name TEXT,
                description TEXT,
                indicators TEXT,
                status TEXT DEFAULT 'new',
                confidence_score INTEGER DEFAULT 0
            )
        ''')
        
        # Baseline data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS baseline_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metric_type TEXT NOT NULL,
                metric_value REAL,
                baseline_value REAL,
                deviation_score REAL
            )
        ''')
        
        # IOC (Indicators of Compromise) table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ioc_matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ioc_type TEXT NOT NULL,
                ioc_value TEXT NOT NULL,
                source TEXT,
                match_context TEXT,
                threat_level TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        self.logger.info("Threat monitoring database initialized")
    
    def load_threat_intelligence(self):
        """Load threat intelligence from the main threat engine database"""
        try:
            if not hasattr(self, '_threat_db_connection'):
                # Connect to main threat database
                threat_conn = sqlite3.connect(self.db_path)
                cursor = threat_conn.cursor()
                
                # Load malicious IPs
                cursor.execute('SELECT indicator_value FROM threat_indicators WHERE indicator_type = "ip"')
                malicious_ips = cursor.fetchall()
                self.threat_patterns['malicious_ips'] = {ip[0] for ip in malicious_ips}
                
                # Load suspicious domains
                cursor.execute('SELECT indicator_value FROM threat_indicators WHERE indicator_type = "domain"')
                domains = cursor.fetchall()
                self.threat_patterns['suspicious_domains'] = {domain[0] for domain in domains}
                
                threat_conn.close()
                
                self.logger.info(f"Loaded {len(self.threat_patterns['malicious_ips'])} malicious IPs and {len(self.threat_patterns['suspicious_domains'])} suspicious domains")
                
        except Exception as e:
            self.logger.error(f"Error loading threat intelligence: {str(e)}")
    
    def analyze_system_metrics(self):
        """Analyze system metrics for anomalies"""
        try:
            # Get recent system metrics from data collector
            conn = sqlite3.connect(self.data_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT cpu_percent, memory_percent, disk_percent, active_processes
                FROM system_metrics 
                ORDER BY timestamp DESC 
                LIMIT 10
            ''')
            
            recent_metrics = cursor.fetchall()
            conn.close()
            
            if not recent_metrics:
                return
            
            # Calculate averages and detect anomalies
            cpu_values = [m[0] for m in recent_metrics if m[0]]
            memory_values = [m[1] for m in recent_metrics if m[1]]
            process_counts = [m[3] for m in recent_metrics if m[3]]
            
            if cpu_values:
                avg_cpu = sum(cpu_values) / len(cpu_values)
                max_cpu = max(cpu_values)
                
                if max_cpu > self.thresholds['cpu_anomaly']:
                    self.create_threat_alert(
                        "RESOURCE_ANOMALY", "HIGH",
                        description=f"Abnormal CPU usage detected: {max_cpu:.1f}% (avg: {avg_cpu:.1f}%)",
                        confidence_score=80
                    )
            
            if memory_values:
                avg_memory = sum(memory_values) / len(memory_values)
                max_memory = max(memory_values)
                
                if max_memory > self.thresholds['memory_anomaly']:
                    self.create_threat_alert(
                        "RESOURCE_ANOMALY", "HIGH",
                        description=f"Abnormal memory usage detected: {max_memory:.1f}% (avg: {avg_memory:.1f}%)",
                        confidence_score=75
                    )
            
            # Process count anomaly detection
            if len(process_counts) >= 5:
                avg_processes = sum(process_counts) / len(process_counts)
                latest_count = process_counts[0]
                
                # Check for significant increase in process count
                if latest_count > avg_processes * 1.5:
                    self.create_threat_alert(
                        "PROCESS_ANOMALY", "MEDIUM",
                        description=f"Unusual increase in process count: {latest_count} (avg: {avg_processes:.0f})",
                        confidence_score=60
                    )
                    
        except Exception as e:
            self.logger.error(f"Error analyzing system metrics: {str(e)}")
    
    def analyze_network_activity(self):
        """Analyze network connections for suspicious activity"""
        try:
            conn = sqlite3.connect(self.data_db_path)
            cursor = conn.cursor()
            
            # Get recent network connections
            cursor.execute('''
                SELECT remote_address, remote_port, process_name, COUNT(*) as conn_count
                FROM network_connections 
                WHERE timestamp > datetime('now', '-5 minutes')
                GROUP BY remote_address, remote_port, process_name
                ORDER BY conn_count DESC
            ''')
            
            connections = cursor.fetchall()
            conn.close()
            
            for conn in connections:
                remote_ip, remote_port, process_name, count = conn
                
                # Check against malicious IP list
                if remote_ip in self.threat_patterns['malicious_ips']:
                    self.create_threat_alert(
                        "MALICIOUS_IP_CONNECTION", "CRITICAL",
                        source_ip=remote_ip,
                        description=f"Connection to known malicious IP: {remote_ip}:{remote_port} via {process_name}",
                        process_name=process_name,
                        confidence_score=95
                    )
                
                # Check for suspicious ports
                if remote_port in [4444, 5555, 6666, 8080, 9999, 31337]:
                    self.create_threat_alert(
                        "SUSPICIOUS_PORT_CONNECTION", "HIGH",
                        source_ip=remote_ip,
                        description=f"Connection to suspicious port: {remote_ip}:{remote_port} via {process_name}",
                        process_name=process_name,
                        confidence_score=70
                    )
                
                # Check for high connection count (potential DDoS or scanning)
                if count > self.thresholds['network_anomaly']:
                    self.create_threat_alert(
                        "NETWORK_ANOMALY", "HIGH",
                        source_ip=remote_ip,
                        description=f"High connection count to {remote_ip}:{remote_port}: {count} connections",
                        process_name=process_name,
                        confidence_score=80
                    )
                
                # Check for connections to foreign countries (simplified)
                if self.is_foreign_ip(remote_ip):
                    self.update_connection_baseline(remote_ip)
                    
        except Exception as e:
            self.logger.error(f"Error analyzing network activity: {str(e)}")
    
    def analyze_process_behavior(self):
        """Analyze running processes for suspicious behavior"""
        try:
            conn = sqlite3.connect(self.data_db_path)
            cursor = conn.cursor()
            
            # Get recent process data
            cursor.execute('''
                SELECT DISTINCT process_name, cpu_percent, memory_percent, command_line, process_id
                FROM process_monitor 
                WHERE timestamp > datetime('now', '-2 minutes')
                AND cpu_percent > 0
                ORDER BY cpu_percent DESC
            ''')
            
            processes = cursor.fetchall()
            conn.close()
            
            for proc in processes:
                proc_name, cpu_pct, mem_pct, cmdline, pid = proc
                
                # Check against suspicious process names
                if any(sus_proc in proc_name.lower() for sus_proc in self.threat_patterns['suspicious_processes']):
                    self.create_threat_alert(
                        "SUSPICIOUS_PROCESS", "HIGH",
                        description=f"Suspicious process detected: {proc_name} (PID: {pid})",
                        process_name=proc_name,
                        indicators=f"Command line: {cmdline[:200]}...",
                        confidence_score=85
                    )
                
                # Check for suspicious command line patterns
                if cmdline and any(sus_cmd in cmdline.lower() for sus_cmd in self.threat_patterns['suspicious_commands']):
                    self.create_threat_alert(
                        "SUSPICIOUS_COMMAND", "MEDIUM",
                        description=f"Suspicious command executed by {proc_name}",
                        process_name=proc_name,
                        indicators=f"Command: {cmdline[:300]}...",
                        confidence_score=70
                    )
                
                # Check for high resource usage by unknown processes
                if cpu_pct > 80 and not self.is_known_system_process(proc_name):
                    self.create_threat_alert(
                        "HIGH_RESOURCE_PROCESS", "MEDIUM",
                        description=f"Unknown process consuming high CPU: {proc_name} ({cpu_pct:.1f}%)",
                        process_name=proc_name,
                        confidence_score=60
                    )
                    
        except Exception as e:
            self.logger.error(f"Error analyzing process behavior: {str(e)}")
    
    def detect_security_events(self):
        """Detect various security events from collected data"""
        try:
            conn = sqlite3.connect(self.data_db_path)
            cursor = conn.cursor()
            
            # Check for rapid process creation (potential malware)
            cursor.execute('''
                SELECT COUNT(*) as proc_count
                FROM process_monitor 
                WHERE timestamp > datetime('now', '-1 minute')
            ''')
            
            recent_process_count = cursor.fetchone()[0]
            
            if recent_process_count > 50:  # More than 50 new processes in 1 minute is suspicious
                self.create_threat_alert(
                    "PROCESS_SPAWN_ANOMALY", "HIGH",
                    description=f"Rapid process creation detected: {recent_process_count} new processes in the last minute.",
                    confidence_score=85
                )

            # Check for failed login attempts (hypothetical, requires data source)
            # This would require an event log or data collector that scrapes system logs
            cursor.execute('''
                SELECT COUNT(*) FROM security_logs WHERE event_type = 'failed_login' AND timestamp > datetime('now', '-5 minutes')
            ''')
            failed_logins = cursor.fetchone()[0]
            if failed_logins > self.thresholds['failed_login_threshold']:
                self.create_threat_alert(
                    "BRUTE_FORCE_ATTEMPT", "HIGH",
                    description=f"Multiple failed login attempts detected: {failed_logins} in the last 5 minutes.",
                    confidence_score=90
                )
                
            # Check for file hash integrity violations (hypothetical)
            # This would require a baseline hash database and a file integrity monitor
            cursor.execute('''
                SELECT file_path, current_hash, baseline_hash FROM file_integrity_monitor WHERE current_hash != baseline_hash
            ''')
            hash_violations = cursor.fetchall()
            for violation in hash_violations:
                file_path, current_hash, baseline_hash = violation
                self.create_threat_alert(
                    "FILE_INTEGRITY_VIOLATION", "CRITICAL",
                    description=f"File integrity check failed for {file_path}",
                    indicators=f"Current Hash: {current_hash[:10]}... | Baseline Hash: {baseline_hash[:10]}...",
                    confidence_score=100
                )
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error detecting security events: {str(e)}")
            
    def create_threat_alert(self, threat_type, severity, source_ip=None, target_ip=None, process_name=None, description=None, indicators=None, confidence_score=0):
        """
        Creates and stores a new threat alert in the database.
        
        Args:
            threat_type (str): The type of threat (e.g., 'RESOURCE_ANOMALY').
            severity (str): The severity level ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL').
            ... other optional parameters for context.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO threat_alerts (threat_type, severity, source_ip, target_ip, process_name, description, indicators, confidence_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (threat_type, severity, source_ip, target_ip, process_name, description, indicators, confidence_score))
            conn.commit()
            conn.close()
            self.logger.warning(f"🚨 Threat Alert: {threat_type} - Severity: {severity} - {description}")
        except Exception as e:
            self.logger.error(f"Failed to create threat alert: {str(e)}")

    def is_known_system_process(self, process_name):
        """
        A simple heuristic to determine if a process is a common system process.
        In a real-world scenario, this would be a more extensive list or a whitelist.
        """
        known_processes = [
            'svchost.exe', 'System', 'explorer.exe', 'csrss.exe', 'wininit.exe',
            'lsass.exe', 'smss.exe', 'dwm.exe', 'services.exe', 'python.exe',
            'bash', 'sshd', 'systemd', 'init', 'kworker'
        ]
        return process_name.lower() in [p.lower() for p in known_processes]

    def is_foreign_ip(self, ip_address):
        """
        A placeholder for a real GeoIP lookup.
        This simplified version checks if the IP is a private/local address.
        """
        try:
            ip = ipaddress.ip_address(ip_address)
            # Check for private IP ranges (e.g., 10.x.x.x, 172.16-31.x.x, 192.168.x.x)
            return not (ip.is_private or ip.is_loopback)
        except ValueError:
            return False

    def update_connection_baseline(self, ip_address):
        """A placeholder for updating a connection baseline for GeoIPs."""
        self.connection_baseline[ip_address] += 1
        # In a real system, you would store and analyze this data to detect
        # deviations from a normal pattern of connections.

    def start_monitoring(self, interval=5):
        """
        Starts the real-time monitoring loop in a background thread.
        
        Args:
            interval (int): The interval in seconds to run each check.
        """
        if self.monitoring_active:
            print("Monitoring is already active.")
            return

        self.monitoring_active = True
        self.logger.info("Starting real-time threat monitoring...")
        
        def monitoring_loop():
            while self.monitoring_active:
                try:
                    self.analyze_system_metrics()
                    self.analyze_network_activity()
                    self.analyze_process_behavior()
                    self.detect_security_events()
                except Exception as e:
                    self.logger.error(f"Error in monitoring loop: {str(e)}")
                time.sleep(interval)

        self.monitor_thread = threading.Thread(target=monitoring_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Stops the monitoring thread."""
        if not self.monitoring_active:
            print("Monitoring is not active.")
            return
        
        self.monitoring_active = False
        self.monitor_thread.join()
        self.logger.info("Threat monitoring stopped.")

if __name__ == "__main__":
    # This is a sample usage block to demonstrate the module.
    # In a full system, a separate process would collect and store data
    # into sentinelit_data.db and sentinelit_threats.db.
    # The monitoring class would then read and analyze that data.
    
    # Placeholder for populating initial data for demonstration purposes
    print("Populating dummy data for demonstration...")
    conn = sqlite3.connect("sentinelit_data.db")
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS system_metrics')
    cursor.execute('DROP TABLE IF EXISTS network_connections')
    cursor.execute('DROP TABLE IF EXISTS process_monitor')
    cursor.execute('DROP TABLE IF EXISTS security_logs')
    conn.commit()
    conn.close()

    conn = sqlite3.connect("sentinelit_data.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_metrics (
            timestamp TIMESTAMP, cpu_percent REAL, memory_percent REAL, active_processes INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS network_connections (
            timestamp TIMESTAMP, remote_address TEXT, remote_port TEXT, process_name TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS process_monitor (
            timestamp TIMESTAMP, process_name TEXT, cpu_percent REAL, memory_percent REAL, command_line TEXT, process_id INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS security_logs (
            timestamp TIMESTAMP, event_type TEXT, message TEXT
        )
    ''')
    conn.commit()
    conn.close()

    # Now, the main class can be instantiated and started
    monitor = SentinelITThreatMonitor()

    # In a real-world scenario, you would have a continuous data collection process
    # running in parallel. For this example, we'll just start the monitor.
    monitor.start_monitoring(interval=2)
    
    # Keep the main thread alive for a while to let the monitor run
    print("Monitoring started. Press Ctrl+C to stop.")
    try:
        time.sleep(20)
    except KeyboardInterrupt:
        pass
    
    monitor.stop_monitoring()
    print("Application shut down.")