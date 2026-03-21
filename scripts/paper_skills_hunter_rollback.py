#!/usr/bin/env python3
"""
ClawHub Paper Skills Hunter
Automatically search, score, and install high-quality paper/research skills from ClawHub
With rollback protection for OpenClaw system
"""

import json
import os
import subprocess
import re
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from pathlib import Path

# Configuration
CLAWHUB_SKILLS_DIR = "/Users/fhjtech/.openclaw/workspace/skills"
LEARNINGS_DIR = "/Users/fhjtech/.openclaw/workspace/.learnings"
SKILLS_REGISTRY = f"{LEARNINGS_DIR}/skills_registry.json"
SCORE_THRESHOLD = 4.8  # 自动安装阈值：4.8分及以上自动安装
INSTALL_LOG = f"{LEARNINGS_DIR}/paper_skills_installed.json"
FEEDBACK_LOG = f"{LEARNINGS_DIR}/paper_skills_feedback.json"
ROLLBACK_LOG = f"{LEARNINGS_DIR}/skill_rollbacks.json"

# OpenClaw health check
def check_openclaw_health():
    """Check if OpenClaw system is running normally"""
    try:
        # Check gateway status
        stdout, stderr, code = run_command("openclaw gateway status 2>&1")
        if code != 0 or "running" not in stdout.lower():
            return False, f"Gateway not running: {stdout}"
        
        # Check if main agent is responsive
        # Try to get session status
        stdout2, stderr2, code2 = run_command("openclaw status 2>&1")
        if code2 != 0:
            return False, f"Status check failed: {stdout2}"
        
        return True, "System healthy"
    except Exception as e:
        return False, f"Health check error: {e}"

def rollback_skill(skill_slug):
    """Rollback (uninstall) a recently installed skill"""
    print(f"🔄 Rolling back skill: {skill_slug}")
    
    # Remove the skill directory
    skill_path = os.path.join(CLAWHUB_SKILLS_DIR, skill_slug.split('/')[-1])
    
    if os.path.exists(skill_path):
        # Backup before removal
        backup_path = f"{skill_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.rename(skill_path, backup_path)
        print(f"   Backed up to: {backup_path}")
    
    # Log the rollback
    log_rollback(skill_slug, "auto_rollback")
    
    return True

def log_rollback(skill_slug, reason):
    """Log rollback event"""
    rollback_entry = {
        "skill_slug": skill_slug,
        "rolled_back_at": datetime.now().isoformat(),
        "reason": reason
    }
    
    if os.path.exists(ROLLBACK_LOG):
        with open(ROLLBACK_LOG, 'r') as f:
            rollbacks = json.load(f)
    else:
        rollbacks = {"rollbacks": []}
    
    rollbacks["rollbacks"].append(rollback_entry)
    
    with open(ROLLBACK_LOG, 'w') as f:
        json.dump(rollbacks, f, indent=2)

def notify_rollback(skill_slug):
    """Send notification about rollback"""
    print(f"📧 Sending rollback notification...")
    
    SMTP_SERVER = "smtp.agentmail.to"
    SMTP_PORT = 465
    EMAIL = "iharvey@agentmail.to"
    PASSWORD = "am_us_cd05b848539e62a8f8399ebdda986586e461a17747f560654aead253d80f3a99"
    
    subject = f"🚨 OpenClaw Skill Rollback Alert - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    body = f"""# 🚨 OpenClaw Skill Rollback Alert

## Rollback Details
- **Skill**: {skill_slug}
- **Time**: {datetime.now().isoformat()}
- **Reason**: System health check failed after installation

## Action Taken
The skill has been automatically rolled back (backed up and removed).

## Next Steps
Please investigate the issue before reinstalling this skill.

---
Havery Auto-Protection System
"""
    
    try:
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = subject
        msg['From'] = EMAIL
        msg['To'] = EMAIL
        
        context = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        context.login(EMAIL, PASSWORD)
        context.sendmail(EMAIL, EMAIL, msg.as_string())
        context.quit()
        print("✅ Rollback notification sent")
    except Exception as e:
        print(f"⚠️  Notification failed: {e}")

def post_install_check(skill_slug):
    """Check system health after installing a new skill"""
    print(f"🔍 Post-install health check for {skill_slug}...")
    
    # Wait a moment for system to stabilize
    import time
    time.sleep(5)
    
    # Check health
    is_healthy, message = check_openclaw_health()
    
    if not is_healthy:
        print(f"❌ System unhealthy after installing {skill_slug}: {message}")
        print(f"   Initiating rollback...")
        rollback_skill(skill_slug)
        notify_rollback(skill_slug)
        return False
    
    print(f"✅ System healthy after installing {skill_slug}")
    return True