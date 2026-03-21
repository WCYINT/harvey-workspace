#!/usr/bin/env python3
"""
EvoMap A2A Heartbeat Script (simple version)
Uses urllib instead of requests
"""

import json
import time
import uuid
from datetime import datetime, timezone
from urllib import request, error
import ssl

# Configuration
HEARTBEAT_URL = "https://evomap.ai/a2a/heartbeat"
NODE_ID = "node_a1b67a1d6a755cc6"
HEARTBEAT_INTERVAL_MS = 900000  # 15 minutes

def send_heartbeat():
    """Send heartbeat to EvoMap hub using urllib"""
    
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
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Sending heartbeat...")
        
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
        
        # Create SSL context that trusts system certificates
        context = ssl.create_default_context()
        
        # Send request
        with request.urlopen(req, timeout=10, context=context) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            print(f"✅ Heartbeat accepted")
            print(f"   Credits: {result.get('credits_balance', 'N/A')}")
            print(f"   Status: {result.get('status', 'N/A')}")
            return True
            
    except error.HTTPError as e:
        print(f"❌ HTTP Error: {e.code} {e.reason}")
        try:
            error_body = e.read().decode('utf-8')
            print(f"   Response: {error_body[:200]}")
        except:
            pass
        return False
    except error.URLError as e:
        print(f"❌ URL Error: {e.reason}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main function - send single heartbeat"""
    print("="*50)
    print("EvoMap A2A Heartbeat")
    print(f"Node ID: {NODE_ID}")
    print("="*50)
    
    success = send_heartbeat()
    
    if success:
        print(f"\n✅ Next heartbeat in {HEARTBEAT_INTERVAL_MS/1000/60:.1f} minutes")
        print("To run continuously, use: python3 evomap_heartbeat_loop.py")
    else:
        print(f"\n❌ Heartbeat failed")
        print("Will retry at next interval")
    
    exit(0 if success else 1)

if __name__ == "__main__":
    main()