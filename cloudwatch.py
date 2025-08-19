
#!/usr/bin/env python3
"""
cloudwatch.py — Unified Cloud Event Manager for SentinelIT

Fixed: thread-safe queue and clean shutdown to prevent _enter_buffered_busy errors
"""

import os
import json
import time
import threading
import atexit
from datetime import datetime
from pathlib import Path
from queue import Queue, Empty

try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
    AWS_AVAILABLE = True
except Exception:
    AWS_AVAILABLE = False

LOG_DIR = Path(os.getenv("SENTINELIT_LOG_DIR", "logs"))
LOG_DIR.mkdir(parents=True, exist_ok=True)

EVENT_LOG_PATH = LOG_DIR / "cloud_events.jsonl"
SYNC_LOG_PATH = LOG_DIR / "cloud_sync_status.txt"

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_REGION = os.getenv("AWS_REGION", "eu-north-1")
S3_BUCKET = os.getenv("S3_BUCKET", "sentinelit-mobile74")

SYNC_INTERVAL = int(os.getenv("CLOUDWATCH_SYNC_INTERVAL", "300"))  # seconds

# --- Thread-safe queue for events ---
event_queue = Queue()
stop_event = threading.Event()

def log_event_to_file(entry: dict):
    try:
        with open(EVENT_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, default=str) + "\n")
    except Exception as e:
        print(f"[CLOUDWATCH] Failed to log event: {e}")

def emit_event(module: str, event_type: str, details: dict):
    """Enqueue event for background processing."""
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "module": module,
        "event_type": event_type,
        "details": details
    }
    event_queue.put(entry)

def _background_worker():
    while not stop_event.is_set():
        try:
            entry = event_queue.get(timeout=1)
            log_event_to_file(entry)
            print(f"[CLOUDWATCH] Event logged: {entry['module']} | {entry['event_type']}")
        except Empty:
            pass
        except Exception as e:
            print(f"[CLOUDWATCH] Worker exception: {e}")
        # sync periodically
        if time.time() % SYNC_INTERVAL < 1:
            sync_to_s3()

def sync_to_s3():
    if not AWS_AVAILABLE or not EVENT_LOG_PATH.exists():
        return
    try:
        session = boto3.session.Session(
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name=AWS_REGION
        )
        s3 = session.resource("s3")
        key_name = f"cloudwatch/{EVENT_LOG_PATH.name}"
        s3.Bucket(S3_BUCKET).upload_file(str(EVENT_LOG_PATH), key_name)

        lines = sum(1 for _ in open(EVENT_LOG_PATH, "r", encoding="utf-8"))
        EVENT_LOG_PATH.unlink(missing_ok=True)

        with open(SYNC_LOG_PATH, "a", encoding="utf-8") as syncf:
            syncf.write(f"Synced {lines} events to S3 at {datetime.utcnow().isoformat()}\n")

        print(f"[CLOUDWATCH] Synced {lines} events to s3://{S3_BUCKET}/{key_name}")
    except (BotoCoreError, ClientError, Exception) as e:
        print(f"[CLOUDWATCH] Sync failed: {e}")

def start_cloudwatch():
    print("[CLOUDWATCH] Starting unified cloud manager...")
    worker = threading.Thread(target=_background_worker, daemon=True)
    worker.start()

    # ensure clean shutdown
    def cleanup():
        stop_event.set()
        worker.join(timeout=5)
    atexit.register(cleanup)



