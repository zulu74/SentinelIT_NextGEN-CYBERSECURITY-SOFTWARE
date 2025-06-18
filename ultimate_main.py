
import os
import threading
import time
import importlib.util
import logging

# Setup logging
logging.basicConfig(
    filename='sentinel_events.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

MODULE_DIR = '.'

# Excluded from auto-scan (setup, icons, launcher, etc.)
EXCLUDED_FILES = {
    'ultimate_main.py', '__init__.py', 'setup.py',
    'sentinel_gui.py', 'tray_icon_runner.py', 'main.py',
    'Setup_sentinelit.iss', 'sentinel_icon.png', 'sentinel_updater.py',
    'sentinelit_autoexec.py', 'README.md'
}

def is_valid_module(file_name):
    return file_name.endswith('.py') and file_name not in EXCLUDED_FILES

def run_module(module_path, module_name):
    try:
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        for entry in ('main', 'run', 'start'):
            if hasattr(mod, entry):
                threading.Thread(target=getattr(mod, entry), daemon=True).start()
                logging.info(f"✅ Started {module_name}")
                return

        logging.warning(f"No runnable entry point in {module_name}")
    except Exception as e:
        logging.error(f"❌ Failed to run {module_name}: {e}")

def main():
    print("🛡️ SentinelIT: Full Defense Mode Launching...")
    py_files = [f for f in os.listdir(MODULE_DIR) if is_valid_module(f)]
    print(f"🔍 Found {len(py_files)} modules to initialize...")

    for py_file in py_files:
        module_path = os.path.join(MODULE_DIR, py_file)
        module_name = os.path.splitext(py_file)[0]
        run_module(module_path, module_name)

    # Always include critical vault modules manually
    for vault_module in ['vaultwatch.py', 'vaultwatch_reboot.py', 'vaultwatch_install.py']:
        try:
            module_name = os.path.splitext(vault_module)[0]
            run_module(os.path.join(MODULE_DIR, vault_module), module_name)
        except Exception as e:
            logging.error(f"❌ Failed to force-load {vault_module}: {e}")

    print("✅ All modules launched. Vault modules forced-in. Logs saved to sentinel_events.log")
    while True:
        time.sleep(10)

if __name__ == "__main__":
    main()
