import os
import hashlib
import json
from datetime import datetime

UEFI_PARTITIONS = ['\\\\.\\PHYSICALDRIVE0']
BASELINE_FILE = 'logs/uefi_baseline.json'
TAMPER_LOG = 'logs/uefi_tamper_log.json'

def get_uefi_signature(partition):
    try:
        with open(partition, 'rb') as f:
            uefi_data = f.read(1024 * 1024)  # Read first 1MB
            hash_obj = hashlib.sha256(uefi_data)
            return hash_obj.hexdigest()
    except Exception as e:
        return None

def save_baseline(signatures):
    with open(BASELINE_FILE, 'w') as f:
        json.dump(signatures, f)

def load_baseline():
    if not os.path.exists(BASELINE_FILE):
        return {}
    with open(BASELINE_FILE, 'r') as f:
        return json.load(f)

def log_tampering(entry):
    logs = []
    if os.path.exists(TAMPER_LOG):
        with open(TAMPER_LOG, 'r') as f:
            logs = json.load(f)
    logs.append(entry)
    with open(TAMPER_LOG, 'w') as f:
        json.dump(logs, f, indent=2)

def check_uefi_tampering():
    baseline = load_baseline()
    tampered = False
    for part in UEFI_PARTITIONS:
        current_sig = get_uefi_signature(part)
        if not current_sig:
            continue
        if part not in baseline:
            baseline[part] = current_sig
            save_baseline(baseline)
        elif baseline[part] != current_sig:
            tampered = True
            log_tampering({
                'timestamp': datetime.utcnow().isoformat(),
                'partition': part,
                'expected': baseline[part],
                'detected': current_sig,
                'event': 'UEFI Tampering Detected'
            })
    if not tampered:
        print('[UEFI Monitor] No tampering detected.')

if __name__ == '__main__':
    check_uefi_tampering()
