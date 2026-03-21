#!/usr/bin/env python3
import smtplib
import ssl
from email.mime.text import MIMEText

# Configuration
SMTP_SERVER = "smtp.163.com"
SMTP_PORT = 587  # Use STARTTLS
SENDER_EMAIL = "wgcapsa@163.com"
SENDER_PASSWORD = "KMRCkfXCMTcHZpGm"
RECIPIENT_EMAIL = "contact@evomap.ai"

# Email content
subject = "Invite Code Request for EvoMap Website Account"
body = """Dear EvoMap Team,

I have successfully registered an AI agent node (node_a1b67a1d6a755cc6) on the EvoMap network and would like to create a website account to monitor its activity and manage credits.

Could you please provide an invite code for website registration?

My agent details:
- Node ID: node_a1b67a1d6a755cc6
- Claim Code: TBKZ-Q9N4 (provided during registration)

Thank you for your assistance.

Best regards,
OpenClaw Assistant"""

try:
    # Create message
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    
    print(f"Connecting to {SMTP_SERVER}:{SMTP_PORT}...")
    
    # Connect with STARTTLS
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
        print("Connected. Starting TLS...")
        server.starttls(context=ssl.create_default_context())
        print("TLS established. Logging in...")
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        print("Login successful. Sending email...")
        server.send_message(msg)
        print("✅ Email sent successfully!")
        
except smtplib.SMTPAuthenticationError as e:
    print(f"❌ Authentication failed: {e}")
    print("\nPossible issues:")
    print("1. Incorrect password")
    print("2. IMAP/SMTP service not enabled in 163.com settings")
    print("3. Need to log into webmail and enable SMTP service")
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"Error type: {type(e).__name__}")