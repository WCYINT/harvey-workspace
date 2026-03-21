#!/usr/bin/env python3
"""
EvoMap A2A Heartbeat Loop
Runs heartbeat every 15 minutes continuously
"""

import json
import time
import uuid
from datetime import datetime, timezone
from urllib import request, error
import ssl
import signal
import sys

# Configuration
HEARTBEAT_URL = "https://evomap.ai/a2a/heartbeat"
NODE_ID = "node_a1b67a1d6a755cc6"
HEARTBEAT_INTERVAL = 900  # 15 minutes in seconds
RETRY_INTERVAL = 300  # 5 minutes if failed
LOG_FILE = "/Users/fhjtech/.openclaw/workspace/evomap_heartbeat.log"

def log_message(message):
    """Log message to console and file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"[{timestamp}] {message}"
    print(full_message)
    
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(full_message + "\n")
    except:
        pass

def send_heartbeat():
    """Send heartbeat to EvoMap hub"""
    
    heartbeat_id = f"heartbeat_{int(time.time())}_{uuid.uuid4().hex[:8]}"
    
    payload = {
        "protocol": "gep-a2a",
        "protocol_version": "1.0.0",
        "message_type": "heartbeat",
        "message_id": heartbeat_id,
        "sender_id": NODE_ID,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "payload": {
            "node_status": "online",
            "credits_balance": 500,
            "last_activity": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
    }
    
    try:
        log_message(f"Sending heartbeat {heartbeat_id}")
        
        # Create request
        req = request.Request(
            HEARTBEAT_URL,
            data=json.dumps(payload).encode('utf-8'),
            headers={
                "Content-Type": "application/json",
                "User-Agent": "EvoMap-Agent/1.0"
            },
            method="POST"
        )
        
        # Create SSL context
        context = ssl.create_default_context()
        
        # Send request
        with request.urlopen(req, timeout=10, context=context) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            log_message(f"Heartbeat accepted - Status: {result.get('status', 'ok')}")
            return True
            
    except error.HTTPError as e:
        log_message(f"HTTP Error: {e.code} {e.reason}")
        return False
    except error.URLError as e:
        log_message(f"URL Error: {e.reason}")
        return False
    except Exception as e:
        log_message(f"Unexpected error: {e}")
        return False

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    log_message("Heartbeat service stopped by user")
    sys.exit(0)

def main():
    """Main loop"""
    signal.signal(signal.SIGINT, signal_handler)
    
    log_message("="*50)
    log_message("EvoMap A2A Heartbeat Service Started")
    log_message(f"Node ID: {NODE_ID}")
    log_message(f"Interval: {HEARTBEAT_INTERVAL/60:.1f} minutes")
    log_message(f"Log file: {LOG_FILE}")
    log_message("="*50)
    
    # Send initial heartbeat
    if not send_heartbeat():
        log_message("Initial heartbeat failed. Will retry at next interval.")
    
    # Main loop
    heartbeat_count = 0
    while True:
        try:
            # Wait for next interval
            log_message(f"Waiting {HEARTBEAT_INTERVAL/60:.1f} minutes...")
            time.sleep(HEARTBEAT_INTERVAL)
            
            # Send heartbeat
            heartbeat_count += 1
            log_message(f"Heartbeat #{heartbeat_count}")
            success = send_heartbeat()
            
            if not success:
                log_message(f"Heartbeat failed. Will retry in {RETRY_INTERVAL/60:.1f} minutes.")
                time.sleep(RETRY_INTERVAL)
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            log_message(f"Loop error: {e}. Retrying in {RETRY_INTERVAL/60:.1f} minutes.")
            time.sleep(RETRY_INTERVAL)
    
    log_message("Heartbeat service stopped")

if __name__ == "__main__":
    main()