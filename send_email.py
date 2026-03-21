#!/usr/bin/env python3
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import ssl

def send_email():
    # SMTP configuration for 163.com
    smtp_server = "smtp.163.com"
    smtp_port = 465  # SSL
    sender_email = "wgcapsa@163.com"
    sender_password = "KMRCkfXCMTcHZpGm"
    
    recipient_email = "contact@evomap.ai"
    
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
    
    # Create message
    msg = MIMEText(body, 'plain', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = f"OpenClaw Assistant <{sender_email}>"
    msg['To'] = recipient_email
    
    try:
        # Create SSL context
        context = ssl.create_default_context()
        
        # Connect to SMTP server
        print(f"Connecting to {smtp_server}:{smtp_port}...")
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            print("Connection established. Logging in...")
            server.login(sender_email, sender_password)
            print("Login successful. Sending email...")
            server.sendmail(sender_email, recipient_email, msg.as_string())
            print("Email sent successfully!")
            return True
            
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

if __name__ == "__main__":
    success = send_email()
    exit(0 if success else 1)