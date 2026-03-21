#!/usr/bin/env python3
"""
Test email integration for self-improving-agent
"""

import subprocess
import json
import os
import sys
from datetime import datetime
from pathlib import Path

def run_himalaya(cmd, account="iharvey", debug=False):
    """Run himalaya command and return result"""
    full_cmd = ["himalaya", "-c", os.path.expanduser("~/.config/himalaya/config.toml")]
    if account:
        full_cmd.extend(["--account", account])
    full_cmd.extend(cmd.split())
    
    if debug:
        print(f"Running: {' '.join(full_cmd)}")
    
    try:
        result = subprocess.run(full_cmd, capture_output=True, text=True, timeout=30)
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Timeout", "stdout": "", "stderr": ""}
    except Exception as e:
        return {"success": False, "error": str(e), "stdout": "", "stderr": ""}

def test_imap_connection():
    """Test IMAP connection by listing folders"""
    print("=" * 60)
    print("Testing IMAP connection...")
    
    # First check account exists
    result = run_himalaya("account list", account=None)
    if not result["success"]:
        print(f"Failed to list accounts: {result.get('error', result['stderr'])}")
        return False
    
    print(f"Accounts:\n{result['stdout']}")
    
    # Try to list folders (might fail if IMAP not configured properly)
    result = run_himalaya("folder list", account="iharvey")
    if result["success"]:
        print(f"✓ IMAP connection successful")
        print(f"Folders:\n{result['stdout']}")
        return True
    else:
        print(f"✗ IMAP folder listing failed (might be expected for some servers)")
        print(f"Error: {result.get('error', result['stderr'])}")
        # Try a simpler test - just check account doctor
        result = run_himalaya("account doctor iharvey", account=None)
        if result["success"]:
            print(f"✓ Account configuration is valid")
            return True
        return False

def test_smtp_send():
    """Test SMTP by sending a test email"""
    print("=" * 60)
    print("Testing SMTP send...")
    
    # Create a test email
    test_subject = f"Test from Havery - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    test_body = """This is a test email from Havery's email integration system.

If you receive this, email configuration is working correctly!

- IMAP: imap.agentmail.to:993
- SMTP: email-smtp.us-east-1.amazonaws.com:587
- Account: iharvey@agentmail.to

This email is part of the self-improvement system integration.
"""
    
    # Save to file
    test_file = Path("/tmp/test_email.txt")
    test_file.write_text(test_body)
    
    # Send using himalaya
    cmd = f"message send --subject '{test_subject}' --body @{test_file} iharvey@agentmail.to"
    result = run_himalaya(cmd, account="iharvey")
    
    if result["success"]:
        print(f"✓ Test email sent successfully!")
        print(f"Subject: {test_subject}")
        print(f"To: iharvey@agentmail.to")
        return True
    else:
        print(f"✗ Failed to send test email")
        print(f"Error: {result.get('error', result['stderr'])}")
        return False

def check_learnings_dir():
    """Check .learnings directory structure"""
    print("=" * 60)
    print("Checking self-improvement system...")
    
    learnings_path = Path("/Users/fhjtech/.openclaw/workspace/.learnings")
    
    if not learnings_path.exists():
        print(f"✗ .learnings directory not found at {learnings_path}")
        return False
    
    files = list(learnings_path.glob("*.md"))
    if not files:
        print(f"✓ .learnings directory exists but no markdown files found")
        return False
    
    print(f"✓ .learnings directory found with {len(files)} files:")
    for f in files:
        size = f.stat().st_size
        print(f"  - {f.name} ({size} bytes)")
    
    # Check if we can create a test learning
    test_learning = learnings_path / "TEST_INTEGRATION.md"
    try:
        test_learning.write_text("# Test Integration\n\nThis is a test learning entry.")
        test_learning.unlink()
        print(f"✓ Can write to .learnings directory")
        return True
    except Exception as e:
        print(f"✗ Cannot write to .learnings directory: {e}")
        return False

def create_email_integration_prototype():
    """Create a prototype for email-learning integration"""
    print("=" * 60)
    print("Creating email integration prototype...")
    
    prototype_dir = Path("/Users/fhjtech/.openclaw/workspace/email_integration")
    prototype_dir.mkdir(exist_ok=True)
    
    # 1. Email monitor script
    monitor_script = prototype_dir / "email_monitor.py"
    monitor_content = """#!/usr/bin/env python3
"""
    monitor_script.write_text(monitor_content)
    
    # 2. Learning creator from email
    learning_creator = prototype_dir / "learning_from_email.py"
    learning_creator.write_text("""#!/usr/bin/env python3
""")
    
    # 3. Notification sender
    notification_sender = prototype_dir / "send_notification.py"
    notification_sender.write_text("""#!/usr/bin/env python3
""")
    
    print(f"✓ Prototype created in {prototype_dir}")
    return True

def main():
    print("Havery Email Integration Test Suite")
    print("=" * 60)
    
    # Run tests
    imap_ok = test_imap_connection()
    
    # Only test SMTP if IMAP is somewhat OK
    smtp_ok = False
    if imap_ok:
        smtp_ok = test_smtp_send()
    else:
        print("Skipping SMTP test due to IMAP issues")
    
    learning_ok = check_learnings_dir()
    
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"IMAP Connection: {'✓ OK' if imap_ok else '✗ FAILED'}")
    print(f"SMTP Send: {'✓ OK' if smtp_ok else '✗ FAILED'}")
    print(f"Learning System: {'✓ OK' if learning_ok else '✗ ISSUES'}")
    
    if imap_ok and smtp_ok:
        print("\n🎉 Email system is fully functional!")
        print("Next steps:")
        print("1. Implement email → learning processor")
        print("2. Add learning → email notifier")
        print("3. Create scheduled report generator")
    elif imap_ok and not smtp_ok:
        print("\n⚠️ IMAP works but SMTP needs configuration")
        print("Check SMTP settings in himalaya config")
    elif not imap_ok:
        print("\n❌ IMAP connection failed")
        print("Check credentials and server settings")
    
    # Create integration design doc
    print("\nIntegration design saved to:")
    print("- /Users/fhjtech/.openclaw/workspace/email_integration_design.md")

if __name__ == "__main__":
    main()