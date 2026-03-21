#!/usr/bin/env python3
import subprocess
import sys

# Email content
email_content = """From: OpenClaw Assistant <wgcapsa@163.com>
To: contact@evomap.ai
Subject: Invite Code Request for EvoMap Website Account

Dear EvoMap Team,

I have successfully registered an AI agent node (node_a1b67a1d6a755cc6) on the EvoMap network and would like to create a website account to monitor its activity and manage credits.

Could you please provide an invite code for website registration?

My agent details:
- Node ID: node_a1b67a1d6a755cc6
- Claim Code: TBKZ-Q9N4 (provided during registration)

Thank you for your assistance.

Best regards,
OpenClaw Assistant"""

try:
    print("Sending email via sendmail...")
    # Send using sendmail with -t (read recipients from mail) and -f (sender)
    result = subprocess.run(
        ["/usr/sbin/sendmail", "-t", "-f", "wgcapsa@163.com"],
        input=email_content.encode('utf-8'),
        capture_output=True,
        timeout=10
    )
    
    if result.returncode == 0:
        print("✅ Email queued for delivery via sendmail")
        print(f"Output: {result.stdout.decode()}")
    else:
        print(f"❌ Sendmail failed with code {result.returncode}")
        print(f"Stderr: {result.stderr.decode()}")
        
except subprocess.TimeoutExpired:
    print("❌ Sendmail command timed out")
except Exception as e:
    print(f"❌ Error: {e}")