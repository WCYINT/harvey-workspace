#!/usr/bin/env python3
"""
EvoMap A2A Heartbeat Script
Sends heartbeat every 15 minutes to keep agent online
"""

import requests
import json
import time
import uuid
from datetime import datetime, timezone
import logging

# Configuration
HEARTBEAT_URL = "https://evomap.ai/a2a/heartbeat"
NODE_ID = "node_a1b67a1d6a755cc6"
HEARTBEAT_INTERVAL_MS = 900000  # 15 minutes
RETRY_INTERVAL = 300  # 5 minutes if failed

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
            "credits_balance": 500,  # Initial balance from registration
            "last_activity": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
    }
    
    try:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Sending heartbeat...")
        response = requests.post(
            HEARTBEAT_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Heartbeat accepted")
            print(f"   Credits: {result.get('credits_balance', 'N/A')}")
            print(f"   Next in: {HEARTBEAT_INTERVAL_MS/1000/60:.1f} minutes")
            return True
        else:
            print(f"❌ Heartbeat failed: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Heartbeat error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def continuous_heartbeat():
    """Run heartbeat loop continuously"""
    print("="*50)
    print("EvoMap A2A Heartbeat Service")
    print(f"Node ID: {NODE_ID}")
    print(f"Interval: {HEARTBEAT_INTERVAL_MS/1000/60:.1f} minutes")
    print("="*50)
    
    # Send initial heartbeat
    if not send_heartbeat():
        print("Initial heartbeat failed. Retrying in 5 minutes...")
        time.sleep(RETRY_INTERVAL)
    
    # Main loop
    while True:
        try:
            # Wait for next heartbeat
            wait_seconds = HEARTBEAT_INTERVAL_MS / 1000
            print(f"\nWaiting {wait_seconds/60:.1f} minutes until next heartbeat...")
            time.sleep(wait_seconds)
            
            # Send heartbeat
            success = send_heartbeat()
            
            if not success:
                print(f"⚠️  Heartbeat failed. Retrying in {RETRY_INTERVAL/60:.1f} minutes...")
                time.sleep(RETRY_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n\nHeartbeat service stopped by user.")
            break
        except Exception as e:
            print(f"\n❌ Loop error: {e}")
            print(f"Retrying in {RETRY_INTERVAL/60:.1f} minutes...")
            time.sleep(RETRY_INTERVAL)

def single_heartbeat():
    """Send a single heartbeat (for testing or cron)"""
    print(f"Sending single heartbeat for node {NODE_ID}...")
    return send_heartbeat()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--single":
        # Single heartbeat mode (for cron)
        success = single_heartbeat()
        exit(0 if success else 1)
    else:
        # Continuous mode
        try:
            continuous_heartbeat()
        except KeyboardInterrupt:
            print("\nHeartbeat service stopped.")
            exit(0)