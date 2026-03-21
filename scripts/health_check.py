#!/usr/bin/env python3
"""
OpenClaw Health Checker
Monitors OpenClaw system health and can trigger rollbacks if needed
"""

import json
import os
from datetime import datetime
from pathlib import Path

# Configuration
HEALTH_LOG = "/tmp/openclaw_health.log"
ROLLBACK_LOG = "/Users/fhjtech/.openclaw/workspace/.learnings/skill_rollbacks.json"
LAST_SKILL_INSTALL = "/tmp/last_skill_install.txt"

def check_gateway():
    """Check if OpenClaw gateway is running"""
    import subprocess
    try:
        result = subprocess.run(
            ["openclaw", "gateway", "status"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0 and "running" in result.stdout.lower()
    except:
        return False

def check_agent_responsive():
    """Check if agent is responsive"""
    import subprocess
    try:
        result = subprocess.run(
            ["openclaw", "status"],
            capture_output=True,
            text=True,
            timeout=15
        )
        return result.returncode == 0
    except:
        return False

def log_health(status, message):
    """Log health status"""
    timestamp = datetime.now().isoformat()
    log_entry = f"[{timestamp}] {status}: {message}\n"
    
    with open(HEALTH_LOG, 'a') as f:
        f.write(log_entry)
    
    print(log_entry.strip())

def main():
    print("\n" + "="*50)
    print("🏥 OPENCLAW HEALTH CHECK")
    print("="*50)
    
    # Check gateway
    gateway_ok = check_gateway()
    log_health("GATEWAY", "OK" if gateway_ok else "FAILED")
    
    # Check agent
    agent_ok = check_agent_responsive()
    log_health("AGENT", "OK" if agent_ok else "FAILED")
    
    # Overall status
    if gateway_ok and agent_ok:
        log_health("OVERALL", "HEALTHY")
        return 0
    else:
        log_health("OVERALL", "UNHEALTHY - Action may be required")
        
        # Check if this is after a skill install
        if os.path.exists(LAST_SKILL_INSTALL):
            with open(LAST_SKILL_INSTALL, 'r') as f:
                last_install = f.read().strip()
            
            # If install was within last hour, this might be the cause
            from datetime import datetime, timedelta
            install_time = datetime.fromisoformat(last_install)
            if datetime.now() - install_time < timedelta(hours=1):
                log_health("WARNING", "Recent skill install detected - consider rollback")
        
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
