# ultimate_launcher.py - Revolutionary Simultaneous Multi-Module Launch System
import subprocess
import threading
import time
import os
import sys
from concurrent.futures import ThreadPoolExecutor
import webbrowser
import psutil
from datetime import datetime

class SentinelITLauncher:
    def __init__(self):
        self.processes = {}
        self.modules = {
            'ai_prediction': 'ai_prediction_engine.py',
            'main_dashboard': 'app.py',
            'ultimate_main': 'ultimate_main.py',
            'data_collector': 'data_collector.py',  # If you have this
            'threat_monitor': 'threat_monitor.py'   # If you have this
        }
        self.urls = [
            'http://localhost:5000/dashboard',
            'http://localhost:5000/network_universe', 
            'http://localhost:5000/attack_visualization',
            'http://localhost:5000/team_collaboration'
        ]
        
    def print_banner(self):
        banner = """
        ╔══════════════════════════════════════════════════════════════╗
        ║                    🛡️  SENTINELIT LAUNCHER 🛡️                    ║
        ║                Revolutionary Cybersecurity Platform          ║
        ║                                                              ║
        ║  🚀 Multi-Module Simultaneous Launch System                  ║
        ║  🌌 3D Network Universe                                      ║
        ║  🧠 AI Quantum Threat Prediction                             ║
        ║  🔥 Real-Time Attack Visualization                           ║
        ║  👥 Multi-Analyst Collaboration                              ║
        ║  📱 AR Mobile Integration (Coming Soon)                      ║
        ║                                                              ║
        ║  ⚡ Status: INITIALIZING QUANTUM DEFENSE GRID...             ║
        ╚══════════════════════════════════════════════════════════════╝
        """
        print("\n" + "="*70)
        print(banner)
        print("="*70 + "\n")
        
    def check_dependencies(self):
        """Check if all required files exist"""
        print("🔍 Checking system dependencies...")
        missing_files = []
        
        for name, filename in self.modules.items():
            if os.path.exists(filename):
                print(f"  ✅ {filename} - Found")
            else:
                print(f"  ❌ {filename} - Missing")
                missing_files.append(filename)
        
        # Check templates directory
        templates_dir = "templates"
        required_templates = [
            "network_universe.html",
            "attack_visualization.html", 
            "team_collaboration.html"
        ]
        
        print(f"\n🔍 Checking {templates_dir} directory...")
        if os.path.exists(templates_dir):
            print(f"  ✅ {templates_dir} directory - Found")
            for template in required_templates:
                template_path = os.path.join(templates_dir, template)
                if os.path.exists(template_path):
                    print(f"  ✅ {template} - Found")
                else:
                    print(f"  ❌ {template} - Missing")
                    missing_files.append(template_path)
        else:
            print(f"  ❌ {templates_dir} directory - Missing")
            
        return len(missing_files) == 0, missing_files
    
    def launch_module(self, name, filename):
        """Launch a single module in a separate process"""
        try:
            print(f"🚀 Starting {name}...")
            
            if filename.endswith('.py'):
                process = subprocess.Popen([
                    sys.executable, filename
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            else:
                print(f"  ⚠️  Unknown file type for {filename}")
                return None
                
            self.processes[name] = process
            print(f"  ✅ {name} launched successfully (PID: {process.pid})")
            return process
            
        except Exception as e:
            print(f"  ❌ Failed to launch {name}: {str(e)}")
            return None
    
    def wait_for_server(self, url, timeout=30):
        """Wait for server to be ready"""
        import requests
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    return True
            except:
                time.sleep(1)
                continue
        return False
    
    def open_dashboards(self):
        """Open all dashboard URLs in browser tabs"""
        print("\n🌐 Opening SentinelIT Dashboard Universe...")
        time.sleep(5)  # Wait for Flask to start
        
        # Check if main server is ready
        if self.wait_for_server('http://localhost:5000'):
            print("  ✅ Main server is ready!")
            
            for i, url in enumerate(self.urls):
                try:
                    print(f"  🚀 Opening: {url}")
                    if i == 0:
                        webbrowser.open(url)  # Main dashboard in default browser
                    else:
                        webbrowser.open_new_tab(url)  # Others in new tabs
                    time.sleep(2)  # Stagger the opening
                except Exception as e:
                    print(f"  ⚠️  Failed to open {url}: {str(e)}")
        else:
            print("  ❌ Server not ready within timeout period")
    
    def monitor_processes(self):
        """Monitor all launched processes"""
        print("\n📊 Process Monitor Active...")
        
        while True:
            time.sleep(10)  # Check every 10 seconds
            
            dead_processes = []
            for name, process in self.processes.items():
                if process and process.poll() is not None:
                    print(f"  ⚠️  Process {name} has terminated (Exit code: {process.returncode})")
                    dead_processes.append(name)
            
            # Remove dead processes
            for name in dead_processes:
                del self.processes[name]
            
            # Print status
            if len(self.processes) > 0:
                print(f"  📈 Active processes: {len(self.processes)}")
                for name in self.processes.keys():
                    print(f"    - {name}: Running")
            else:
                print("  ❌ No active processes remaining")
                break
    
    def launch_all(self):
        """Launch all modules simultaneously"""
        self.print_banner()
        
        # Check dependencies
        deps_ok, missing = self.check_dependencies()
        if not deps_ok:
            print(f"\n❌ Missing required files:")
            for file in missing:
                print(f"  - {file}")
            print("\n Please ensure all files are present before launching.")
            return False
        
        print("\n🚀 INITIATING SIMULTANEOUS LAUNCH SEQUENCE...")
        print("=" * 60)
        
        # Launch all modules simultaneously using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=len(self.modules)) as executor:
            futures = {}
            
            for name, filename in self.modules.items():
                if os.path.exists(filename):
                    future = executor.submit(self.launch_module, name, filename)
                    futures[future] = name
            
            # Wait for all launches to complete
            for future in futures:
                future.result()
        
        print(f"\n✅ Launch sequence complete! {len(self.processes)} modules running")
        print("=" * 60)
        
        # Open browser dashboards in a separate thread
        browser_thread = threading.Thread(target=self.open_dashboards)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Start process monitor in a separate thread
        monitor_thread = threading.Thread(target=self.monitor_processes)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        print("\n🎮 CONTROL CENTER ACTIVE")
        print("=" * 30)
        print("Commands:")
        print("  's' - Show status")
        print("  'r' - Restart all modules")  
        print("  'b' - Open browsers again")
        print("  'q' - Shutdown all modules")
        print("=" * 30)
        
        # Command loop
        while True:
            try:
                cmd = input("\nSentinelIT> ").strip().lower()
                
                if cmd == 'q':
                    self.shutdown_all()
                    break
                elif cmd == 's':
                    self.show_status()
                elif cmd == 'r':
                    self.restart_all()
                elif cmd == 'b':
                    browser_thread = threading.Thread(target=self.open_dashboards)
                    browser_thread.daemon = True
                    browser_thread.start()
                else:
                    print("Unknown command. Use 's', 'r', 'b', or 'q'")
                    
            except KeyboardInterrupt:
                print("\n\n🛑 Shutdown signal received...")
                self.shutdown_all()
                break
    
    def show_status(self):
        """Show status of all processes"""
        print(f"\n📊 SENTINELIT SYSTEM STATUS - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 50)
        
        if not self.processes:
            print("  ❌ No active processes")
            return
        
        for name, process in self.processes.items():
            if process and process.poll() is None:
                try:
                    p = psutil.Process(process.pid)
                    cpu = p.cpu_percent()
                    memory = p.memory_info().rss / 1024 / 1024  # MB
                    print(f"  ✅ {name:15} - PID: {process.pid:5} | CPU: {cpu:5.1f}% | RAM: {memory:6.1f}MB")
                except:
                    print(f"  ✅ {name:15} - PID: {process.pid:5} | Status: Running")
            else:
                print(f"  ❌ {name:15} - Not running")
    
    def restart_all(self):
        """Restart all modules"""
        print("\n🔄 Restarting all modules...")
        self.shutdown_all(show_message=False)
        time.sleep(2)
        
        # Relaunch
        with ThreadPoolExecutor(max_workers=len(self.modules)) as executor:
            futures = {}
            for name, filename in self.modules.items():
                if os.path.exists(filename):
                    future = executor.submit(self.launch_module, name, filename)
                    futures[future] = name
            
            for future in futures:
                future.result()
        
        print("✅ Restart complete!")
    
    def shutdown_all(self, show_message=True):
        """Shutdown all launched processes"""
        if show_message:
            print("\n🛑 Shutting down all SentinelIT modules...")
        
        for name, process in self.processes.items():
            if process and process.poll() is None:
                print(f"  🔻 Terminating {name}...")
                try:
                    process.terminate()
                    process.wait(timeout=5)
                    print(f"    ✅ {name} terminated gracefully")
                except subprocess.TimeoutExpired:
                    print(f"    ⚠️  Force killing {name}...")
                    process.kill()
                    print(f"    ✅ {name} force terminated")
                except Exception as e:
                    print(f"    ❌ Error terminating {name}: {str(e)}")
        
        self.processes.clear()
        if show_message:
            print("\n✅ All modules shutdown complete")
            print("🛡️  SentinelIT Launcher terminated")

def main():
    """Main entry point"""
    launcher = SentinelITLauncher()
    launcher.launch_all()

if __name__ == "__main__":
    main()