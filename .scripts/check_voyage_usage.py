#!/usr/bin/env python3
"""
Check Voyage AI usage every 2 days
Usage: python3 check_voyage_usage.py
"""

import subprocess
import os
import json
import time

AGENT_BROWSER = "npx agent-browser"
SESSION = "voyageai-usage"
DASHBOARD_URL = "https://dashboard.voyageai.com/organization/usage"
OUTPUT_FILE = "/Users/fhjtech/.openclaw/logs/voyage_usage_check.log"
STATE_FILE = "/Users/fhjtech/.openclaw/workspace/voyageai-auth.json"

def run(cmd, timeout=30):
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True, timeout=timeout
    )
    return result.stdout, result.stderr, result.returncode

def check_usage():
    log = []
    log.append(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting Voyage AI usage check")
    
    # Check if state file exists
    if not os.path.exists(STATE_FILE):
        log.append("ERROR: Auth state file not found, need to login first")
        return "\n".join(log), None
    
    # Open browser with existing auth state
    cmd = f'{AGENT_BROWSER} --session {SESSION} open {DASHBOARD_URL}'
    stdout, stderr, code = run(cmd, timeout=20)
    
    # Wait for page load
    time.sleep(5)
    
    # Click Free Token tab
    cmd = f'{AGENT_BROWSER} --session {SESSION} snapshot -i'
    stdout, stderr, code = run(cmd, timeout=15)
    
    # Find and click Free Token tab
    if 'ref=e19' in stdout or 'Free Token' in stdout:
        cmd = f'{AGENT_BROWSER} --session {SESSION} click @e19'
        run(cmd, timeout=10)
        time.sleep(3)
    
    # Get usage text
    cmd = f'{AGENT_BROWSER} --session {SESSION} get text @e13'
    stdout, stderr, code = run(cmd, timeout=10)
    
    # Parse voyage-4-large usage
    usage_text = stdout.strip()
    log.append(f"Usage text: {usage_text}")
    
    # Extract voyage-4-large data
    voyage_4_large_used = None
    voyage_4_large_total = None
    
    lines = usage_text.split('\n')
    for i, line in enumerate(lines):
        if 'voyage-4-large' in line.lower():
            # Next lines should be Tokens, Used, Remained
            for j in range(i+1, min(i+10, len(lines))):
                if 'Used:' in lines[j]:
                    try:
                        used_str = lines[j].split('Used:')[1].strip().replace(',', '')
                        voyage_4_large_used = int(used_str)
                    except:
                        pass
                if 'Remained:' in lines[j]:
                    try:
                        remained_str = lines[j].split('Remained:')[1].strip().replace(',', '')
                        voyage_4_large_total = int(remained_str)
                    except:
                        pass
    
    # Calculate percentage
    if voyage_4_large_used and voyage_4_large_total:
        pct = (voyage_4_large_used / voyage_4_large_total) * 100
        log.append(f"voyage-4-large: {voyage_4_large_used:,} / {voyage_4_large_total:,} ({pct:.2f}%)")
        
        if pct >= 95:
            log.append(f"⚠️ WARNING: Usage at {pct:.2f}%, consider switching models!")
            subject = f"Voyage AI Usage Warning: {pct:.2f}%"
            body = f"voyage-4-large usage has reached {pct:.2f}%. Consider switching models."
        else:
            log.append(f"✅ Usage normal at {pct:.2f}%")
            subject = f"Voyage AI Usage Report: {pct:.2f}%"
            body = f"voyage-4-large: {voyage_4_large_used:,} / {voyage_4_large_total:,} ({pct:.2f}%)"
    else:
        log.append("Could not parse voyage-4-large usage")
        subject = "Voyage AI Usage Check Failed"
        body = "Could not parse usage data. Check dashboard manually."
    
    # Close browser
    run(f'{AGENT_BROWSER} --session {SESSION} close', timeout=5)
    
    # Save log
    with open(OUTPUT_FILE, 'a') as f:
        f.write("\n".join(log) + "\n")
    
    return "\n".join(log), subject

if __name__ == "__main__":
    result, subject = check_usage()
    print(result)
    if subject:
        print(f"\nSubject: {subject}")
