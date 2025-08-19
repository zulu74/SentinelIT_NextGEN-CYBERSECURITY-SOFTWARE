# real_threat_engine.py - Enterprise-Grade Real Threat Detection System
import requests
import json
import sqlite3
import threading
import time
import hashlib
import socket
import subprocess
import psutil
import ipaddress
import re
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import dns.resolver
import whois
import geoip2.database
import shodan
import os
import logging
from collections import defaultdict, deque
import numpy as np
from sklearn.ensemble import IsolationForest
import pandas as pd

class RealThreatIntelligence:
    def __init__(self):
        self.db_path = "sentinelit_threats.db"
        self.threat_feeds = {
            'abuse_ch': 'https://feodotracker.abuse.ch/downloads/ipblocklist.json',
            'malware_domains': 'https://mirror1.malwaredomains.com/files/domains.txt',
            'emerging_threats': 'https://rules.emergingthreats.net/fwrules/emerging-Block-IPs.txt',
            'phishing_db': 'https://phishing.army/download/phishing_army_blocklist_extended.txt',
            'tor_exits': 'https://check.torproject.org/torbulkexitlist',
            'alienvault': 'https://reputation.alienvault.com/reputation.data'
        }
        
        # Real API keys (users will need to add their own)
        self.api_keys = {
            'virustotal': os.getenv('VIRUSTOTAL_API_KEY'),
            'shodan': os.getenv('SHODAN_API_KEY'), 
            'abuseipdb': os.getenv('ABUSEIPDB_API_KEY'),
            'greynoise': os.getenv('GREYNOISE_API_KEY')
        }
        
        self.threat_indicators = defaultdict(list)
        self.network_baseline = {}
        self.anomaly_detector = IsolationForest(contamination=0.1)
        self.connection_history = deque(maxlen=10000)
        self.dns_cache = {}
        self.geolocation_cache = {}
        
        self.setup_database()
        self.setup_logging()
        
    def setup_logging(self):
        """Setup comprehensive logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('sentinelit_threats.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('SentinelIT-ThreatEngine')
        
    def setup_database(self):
        """Create database for threat intelligence storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Threat indicators table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS threat_indicators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                indicator_type TEXT NOT NULL,
                indicator_value TEXT NOT NULL UNIQUE,
                threat_level TEXT NOT NULL,
                source TEXT NOT NULL,
                description TEXT,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                confidence_score INTEGER DEFAULT 0
            )
        ''')
        
        # Network events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS network_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source_ip TEXT NOT NULL,
                destination_ip TEXT,
                source_port INTEGER,
                destination_port INTEGER,
                protocol TEXT,
                bytes_sent INTEGER DEFAULT 0,
                bytes_received INTEGER DEFAULT 0,
                connection_duration REAL,
                threat_score INTEGER DEFAULT 0,
                event_type TEXT,
                details TEXT
            )
        ''')
        
        # Detected threats table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detected_threats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                threat_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                source_ip TEXT,
                target_ip TEXT,
                indicator TEXT,
                description TEXT,
                mitigation_action TEXT,
                status TEXT DEFAULT 'new'
            )
        ''')
        
        conn.commit()
        conn.close()
        self.logger.info("Database initialized successfully")
        
    def fetch_threat_feeds(self):
        """Download and parse real threat intelligence feeds"""
        self.logger.info("Fetching real threat intelligence feeds...")
        
        def fetch_feed(name, url):
            try:
                self.logger.info(f"Downloading {name} feed...")
                response = requests.get(url, timeout=30, headers={
                    'User-Agent': 'SentinelIT-ThreatEngine/1.0'
                })
                
                if response.status_code == 200:
                    self.parse_threat_feed(name, response.text, url)
                    self.logger.info(f"✅ {name} feed processed successfully")
                else:
                    self.logger.warning(f"⚠️ Failed to fetch {name}: HTTP {response.status_code}")
                    
            except Exception as e:
                self.logger.error(f"❌ Error fetching {name}: {str(e)}")
        
        # Use ThreadPoolExecutor for concurrent downloads
        with ThreadPoolExecutor(max_workers=5) as executor:
            for name, url in self.threat_feeds.items():
                executor.submit(fetch_feed, name, url)
    
    def parse_threat_feed(self, feed_name, content, url):
        """Parse different types of threat feeds"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if feed_name == 'abuse_ch' and content.startswith('{'):
                # JSON format
                data = json.loads(content)
                for ip_info in data:
                    if 'ip' in ip_info:
                        self.store_threat_indicator(
                            cursor, 'ip', ip_info['ip'], 'high',
                            feed_name, f"Malware C2: {ip_info.get('malware', 'Unknown')}"
                        )
                        
            elif 'domains' in feed_name or 'phishing' in feed_name:
                # Domain lists
                domains = [line.strip() for line in content.split('\n') 
                          if line.strip() and not line.startswith('#')]
                for domain in domains[:1000]:  # Limit to prevent overload
                    if self.is_valid_domain(domain):
                        self.store_threat_indicator(
                            cursor, 'domain', domain, 'medium',
                            feed_name, "Malicious domain"
                        )
            
            elif 'tor_exits' in feed_name:
                # TOR exit nodes
                ips = [line.strip() for line in content.split('\n') 
                       if line.strip() and self.is_valid_ip(line.strip())]
                for ip in ips:
                    self.store_threat_indicator(
                        cursor, 'ip', ip, 'low',
                        feed_name, "TOR exit node"
                    )
                    
            else:
                # Generic IP lists
                ips = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', content)
                for ip in ips[:2000]:  # Limit to prevent overload
                    if self.is_valid_ip(ip):
                        self.store_threat_indicator(
                            cursor, 'ip', ip, 'medium',
                            feed_name, "Suspicious IP"
                        )
                        
        except Exception as e:
            self.logger.error(f"Error parsing {feed_name}: {str(e)}")
        
        conn.commit()
        conn.close()
    
    def store_threat_indicator(self, cursor, ind_type, value, level, source, desc):
        """Store threat indicator in database"""
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO threat_indicators 
                (indicator_type, indicator_value, threat_level, source, description, last_updated)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (ind_type, value, level, source, desc))
        except Exception as e:
            self.logger.error(f"Error storing indicator {value}: {str(e)}")
    
    def is_valid_ip(self, ip):
        """Validate IP address"""
        try:
            ipaddress.ip_address(ip)
            # Exclude private IPs from threat feeds
            ip_obj = ipaddress.ip_address(ip)
            return not (ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_multicast)
        except:
            return False
    
    def is_valid_domain(self, domain):
        """Validate domain name"""
        pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
        return re.match(pattern, domain) is not None
    
    def monitor_network_connections(self):
        """Monitor real network connections on the system"""
        self.logger.info("Starting real-time network monitoring...")
        
        while True:
            try:
                connections = psutil.net_connections(kind='inet')
                current_time = datetime.now()
                
                for conn in connections:
                    if conn.status == psutil.CONN_ESTABLISHED and conn.raddr:
                        # Analyze each connection
                        threat_score = self.analyze_connection(conn)
                        
                        # Store in database if significant
                        if threat_score > 0:
                            self.store_network_event(conn, threat_score, current_time)
                        
                        # Add to connection history for baseline learning
                        self.connection_history.append({
                            'timestamp': current_time,
                            'remote_ip': conn.raddr.ip,
                            'remote_port': conn.raddr.port,
                            'local_port': conn.laddr.port,
                            'threat_score': threat_score
                        })
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                self.logger.error(f"Network monitoring error: {str(e)}")
                time.sleep(30)  # Wait longer if error
    
    def analyze_connection(self, conn):
        """Analyze individual network connection for threats"""
        threat_score = 0
        remote_ip = conn.raddr.ip
        remote_port = conn.raddr.port
        
        try:
            # Check against threat intelligence database
            if self.is_malicious_ip(remote_ip):
                threat_score += 80
                self.log_threat("Malicious IP Connection", "high", remote_ip)
            
            # Check for suspicious ports
            if self.is_suspicious_port(remote_port):
                threat_score += 30
            
            # Geographic analysis
            geo_info = self.get_geolocation(remote_ip)
            if geo_info and geo_info.get('country') in ['CN', 'RU', 'KP', 'IR']:
                threat_score += 20  # Higher scrutiny for certain countries
            
            # DNS reputation check
            if self.has_malicious_dns(remote_ip):
                threat_score += 50
            
            # Behavioral analysis
            if self.is_anomalous_connection(remote_ip, remote_port):
                threat_score += 40
                
        except Exception as e:
            self.logger.error(f"Connection analysis error: {str(e)}")
        
        return min(threat_score, 100)  # Cap at 100
    
    def is_malicious_ip(self, ip):
        """Check IP against threat intelligence database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT threat_level FROM threat_indicators 
            WHERE indicator_type = 'ip' AND indicator_value = ?
        ''', (ip,))
        
        result = cursor.fetchone()
        conn.close()
        
        return result is not None and result[0] in ['high', 'critical']
    
    def is_suspicious_port(self, port):
        """Check for commonly abused ports"""
        suspicious_ports = {
            # Remote access trojans
            1337, 31337, 12345, 54321, 9999,
            # Backdoors
            2023, 4444, 5555, 6666, 7777,
            # Bitcoin/Crypto mining
            8333, 9333, 18333,
            # Tor
            9001, 9030,
            # Uncommon high ports often used maliciously
        }
        
        return port in suspicious_ports or port > 50000
    
    def get_geolocation(self, ip):
        """Get geolocation information for IP"""
        if ip in self.geolocation_cache:
            return self.geolocation_cache[ip]
        
        try:
            # Try to use MaxMind GeoLite2 if available
            if os.path.exists('GeoLite2-Country.mmdb'):
                with geoip2.database.Reader('GeoLite2-Country.mmdb') as reader:
                    response = reader.country(ip)
                    geo_info = {
                        'country': response.country.iso_code,
                        'country_name': response.country.name
                    }
            else:
                # Fallback to free API (limited requests)
                response = requests.get(f'http://ip-api.com/json/{ip}', timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    geo_info = {
                        'country': data.get('countryCode'),
                        'country_name': data.get('country'),
                        'city': data.get('city'),
                        'isp': data.get('isp')
                    }
                else:
                    geo_info = None
            
            self.geolocation_cache[ip] = geo_info
            return geo_info
            
        except Exception as e:
            self.logger.error(f"Geolocation lookup error for {ip}: {str(e)}")
            return None
    
    def has_malicious_dns(self, ip):
        """Check DNS reputation of IP"""
        if ip in self.dns_cache:
            return self.dns_cache[ip]
        
        try:
            # Reverse DNS lookup
            hostname = socket.gethostbyaddr(ip)[0]
            
            # Check for suspicious domain patterns
            suspicious_patterns = [
                r'\.tk$', r'\.ml$', r'\.ga$', r'\.cf$',  # Free TLDs often abused
                r'dyndns', r'no-ip', r'ddns',  # Dynamic DNS
                r'[0-9]{8,}',  # Long numbers in domain
                r'[a-z]{20,}',  # Very long random strings
            ]
            
            is_malicious = any(re.search(pattern, hostname, re.IGNORECASE) 
                             for pattern in suspicious_patterns)
            
            self.dns_cache[ip] = is_malicious
            return is_malicious
            
        except Exception:
            self.dns_cache[ip] = False
            return False
    
    def is_anomalous_connection(self, ip, port):
        """Detect anomalous connections using machine learning"""
        if len(self.connection_history) < 100:
            return False  # Need baseline data
        
        try:
            # Create feature vector for current connection
            current_features = self.extract_connection_features(ip, port)
            
            # Train anomaly detector on historical data if needed
            if not hasattr(self.anomaly_detector, 'offset_'):
                historical_features = [
                    self.extract_connection_features(h['remote_ip'], h['remote_port'])
                    for h in list(self.connection_history)[-500:]  # Last 500 connections
                ]
                self.anomaly_detector.fit(historical_features)
            
            # Predict if current connection is anomalous
            prediction = self.anomaly_detector.predict([current_features])
            return prediction[0] == -1  # -1 indicates anomaly
            
        except Exception as e:
            self.logger.error(f"Anomaly detection error: {str(e)}")
            return False
    
    def extract_connection_features(self, ip, port):
        """Extract numerical features from connection for ML analysis"""
        try:
            # Convert IP to numerical representation
            ip_int = int(ipaddress.ip_address(ip))
            
            # Port category
            port_category = 0
            if port < 1024:
                port_category = 1  # Well-known ports
            elif port < 49152:
                port_category = 2  # Registered ports
            else:
                port_category = 3  # Dynamic/private ports
            
            # Time-based features
            hour = datetime.now().hour
            is_business_hours = 1 if 9 <= hour <= 17 else 0
            
            return [ip_int % 1000000, port, port_category, hour, is_business_hours]
            
        except Exception:
            return [0, port, 0, 0, 0]
    
    def store_network_event(self, conn, threat_score, timestamp):
        """Store network event in database"""
        try:
            conn_db = sqlite3.connect(self.db_path)
            cursor = conn_db.cursor()
            
            cursor.execute('''
                INSERT INTO network_events 
                (timestamp, source_ip, destination_ip, source_port, destination_port, 
                 protocol, threat_score, event_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp, conn.laddr.ip, conn.raddr.ip,
                conn.laddr.port, conn.raddr.port,
                'TCP' if conn.type == socket.SOCK_STREAM else 'UDP',
                threat_score, 'connection'
            ))
            
            conn_db.commit()
            conn_db.close()
            
        except Exception as e:
            self.logger.error(f"Error storing network event: {str(e)}")
    
    def log_threat(self, threat_type, severity, indicator, description=""):
        """Log detected threat"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO detected_threats 
                (threat_type, severity, source_ip, indicator, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (threat_type, severity, indicator, indicator, description))
            
            conn.commit()
            conn.close()
            
            self.logger.warning(f"🚨 THREAT DETECTED: {threat_type} - {severity.upper()} - {indicator}")
            
        except Exception as e:
            self.logger.error(f"Error logging threat: {str(e)}")
    
    def get_recent_threats(self, hours=24):
        """Get recently detected threats"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM detected_threats 
            WHERE timestamp > datetime('now', '-{} hours')
            ORDER BY timestamp DESC
        '''.format(hours))
        
        threats = cursor.fetchall()
        conn.close()
        
        return threats
    
    def get_threat_statistics(self):
        """Get comprehensive threat statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Threat indicators count
        cursor.execute('SELECT COUNT(*) FROM threat_indicators')
        stats['total_indicators'] = cursor.fetchone()[0]
        
        # Recent threats (last 24h)
        cursor.execute('''
            SELECT COUNT(*) FROM detected_threats 
            WHERE timestamp > datetime('now', '-24 hours')
        ''')
        stats['threats_24h'] = cursor.fetchone()[0]
        
        # Threats by severity
        cursor.execute('''
            SELECT severity, COUNT(*) FROM detected_threats 
            WHERE timestamp > datetime('now', '-24 hours')
            GROUP BY severity
        ''')
        stats['threats_by_severity'] = dict(cursor.fetchall())
        
        # Top threat sources
        cursor.execute('''
            SELECT source_ip, COUNT(*) as count FROM detected_threats 
            WHERE timestamp > datetime('now', '-24 hours')
            GROUP BY source_ip 
            ORDER BY count DESC 
            LIMIT 10
        ''')
        stats['top_threat_sources'] = cursor.fetchall()
        
        conn.close()
        return stats
    
    def start_threat_engine(self):
        """Start the complete threat intelligence engine"""
        self.logger.info("🚀 Starting SentinelIT Real Threat Intelligence Engine...")
        
        # Initial threat feed download
        self.fetch_threat_feeds()
        
        # Start network monitoring thread
        network_thread = threading.Thread(target=self.monitor_network_connections)
        network_thread.daemon = True
        network_thread.start()
        
        # Start periodic threat feed updates
        def update_feeds():
            while True:
                time.sleep(3600)  # Update every hour
                self.fetch_threat_feeds()
        
        feed_thread = threading.Thread(target=update_feeds)
        feed_thread.daemon = True
        feed_thread.start()
        
        self.logger.info("✅ Real Threat Intelligence Engine is running!")
        self.logger.info("📊 Monitoring network connections for real threats...")
        self.logger.info("🛡️ Threat feeds updating every hour...")
        
        return {
            'status': 'running',
            'threads': ['network_monitor', 'feed_updater'],
            'database': self.db_path
        }

# API Integration Functions for Enhanced Threat Intelligence
class ThreatAPIIntegrator:
    def __init__(self, api_keys):
        self.api_keys = api_keys
        
    def check_virustotal(self, indicator, indicator_type='ip'):
        """Check indicator against VirusTotal"""
        if not self.api_keys.get('virustotal'):
            return None
            
        try:
            if indicator_type == 'ip':
                url = f"https://www.virustotal.com/vtapi/v2/ip-address/report"
            else:
                url = f"https://www.virustotal.com/vtapi/v2/domain/report"
            
            params = {
                'apikey': self.api_keys['virustotal'],
                indicator_type: indicator
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'positives': data.get('positives', 0),
                    'total': data.get('total', 0),
                    'permalink': data.get('permalink', ''),
                    'scan_date': data.get('scan_date', '')
                }
                
        except Exception as e:
            logging.error(f"VirusTotal API error: {str(e)}")
            
        return None
    
    def check_abuseipdb(self, ip):
        """Check IP against AbuseIPDB"""
        if not self.api_keys.get('abuseipdb'):
            return None
            
        try:
            url = "https://api.abuseipdb.com/api/v2/check"
            headers = {
                'Key': self.api_keys['abuseipdb'],
                'Accept': 'application/json'
            }
            params = {
                'ipAddress': ip,
                'maxAgeInDays': 90,
                'verbose': ''
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json().get('data', {})
                return {
                    'confidence': data.get('abuseConfidencePercentage', 0),
                    'usage_type': data.get('usageType', ''),
                    'country': data.get('countryCode', ''),
                    'is_whitelisted': data.get('isWhitelisted', False)
                }
                
        except Exception as e:
            logging.error(f"AbuseIPDB API error: {str(e)}")
            
        return None

def main():
    """Main function to start the real threat engine"""
    threat_engine = RealThreatIntelligence()
    
    print("🛡️  SentinelIT Real Threat Intelligence Engine")
    print("=" * 50)
    print("This engine provides REAL threat detection:")
    print("✅ Live threat intelligence feeds")
    print("✅ Real network connection monitoring") 
    print("✅ Machine learning anomaly detection")
    print("✅ Geographic and DNS analysis")
    print("✅ API integration with major threat databases")
    print("=" * 50)
    
    # Start the engine
    status = threat_engine.start_threat_engine()
    print(f"Status: {status}")
    
    try:
        while True:
            # Print statistics every 5 minutes
            time.sleep(300)
            stats = threat_engine.get_threat_statistics()
            print(f"\n📊 Threat Statistics:")
            print(f"   Total Indicators: {stats['total_indicators']}")
            print(f"   Threats (24h): {stats['threats_24h']}")
            print(f"   By Severity: {stats.get('threats_by_severity', {})}")
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Threat Intelligence Engine...")

if __name__ == "__main__":
    main()