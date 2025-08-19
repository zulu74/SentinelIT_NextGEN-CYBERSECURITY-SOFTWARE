# sentinel_agent.py
import psutil
import requests
import time
import json
import hashlib
from pathlib import Path

class SentinelAgent:
    def __init__(self, server_url, agent_key):
        self.server_url = server_url
        self.agent_key = agent_key
        self.computer_id = self.get_computer_id()
    
    def collect_system_metrics(self):
        return {
            'computer_id': self.computer_id,
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'running_processes': len(psutil.pids()),
            'network_connections': len(psutil.net_connections()),
            'timestamp': time.time()
        }
    
    def detect_threats(self):
        threats = []
        
        # Check for suspicious processes
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            if proc.info['cpu_percent'] > 80:  # High CPU usage
                threats.append({
                    'type': 'High CPU Process',
                    'severity': 'medium',
                    'details': f"Process {proc.info['name']} using {proc.info['cpu_percent']}% CPU"
                })
        
        return threats
    
    def send_data(self, data):
        try:
            response = requests.post(
                f"{self.server_url}/api/agent_data",
                json=data,
                headers={'Authorization': f'Bearer {self.agent_key}'},
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Failed to send data: {e}")
            return False
    
    def run(self):
        while True:
            # Collect system data
            metrics = self.collect_system_metrics()
            threats = self.detect_threats()
            
            # Send to server
            data = {
                'metrics': metrics,
                'threats': threats
            }
            
            self.send_data(data)
            time.sleep(30)  # Send data every 30 seconds

if __name__ == "__main__":
    agent = SentinelAgent("https://your-server.com", "agent-key-123")
    agent.run()