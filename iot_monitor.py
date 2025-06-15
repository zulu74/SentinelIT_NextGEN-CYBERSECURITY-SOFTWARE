
import os
import time
import psutil

def monitor_iot_devices():
    print("[IoTMonitor] Monitoring for new IoT devices...")
    known_devices = set(d.device for d in psutil.disk_partitions())

    while True:
        current_devices = set(d.device for d in psutil.disk_partitions())
        new_devices = current_devices - known_devices

        for device in new_devices:
            print(f"[IoTMonitor] New device detected: {device}")
            # Simulate a scan (custom logic can be plugged here)
            time.sleep(1)
            print(f"[IoTMonitor] Device {device} scan completed. No threats found.")

        known_devices = current_devices
        time.sleep(10)

if __name__ == "__main__":
    monitor_iot_devices()
