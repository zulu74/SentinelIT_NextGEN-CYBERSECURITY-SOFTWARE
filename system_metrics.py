import psutil
from datetime import datetime

def get_system_metrics():
    try:
        return {
            'cpu_usage': psutil.cpu_percent(interval=1),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'network_io': {
                'bytes_sent': psutil.net_io_counters().bytes_sent,
                'bytes_recv': psutil.net_io_counters().bytes_recv
            },
            'uptime': datetime.now() - datetime.fromtimestamp(psutil.boot_time())
        }
    except Exception as e:
        print(f"[SystemMetrics] Error collecting metrics: {e}")
        return {
            'cpu_usage': 0,
            'memory_usage': 0,
            'disk_usage': 0,
            'network_io': {'bytes_sent': 0, 'bytes_recv': 0},
            'uptime': datetime.now() - datetime.now()
        }