#!/usr/bin/env python3
"""
Test SMTP connection directly to Amazon SES
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys

def test_smtp_connection(host, port, username, password, use_ssl=True, use_starttls=False):
    """Test SMTP connection with different configurations"""
    print(f"Testing SMTP connection to {host}:{port}")
    print(f"Username: {username}")
    print(f"SSL: {use_ssl}, STARTTLS: {use_starttls}")
    
    try:
        if use_ssl:
            # SSL/TLS connection (port 465)
            context = ssl.create_default_context()
            server = smtplib.SMTP_SSL(host, port, context=context, timeout=10)
            print(f"✓ Connected via SSL to {host}:{port}")
        else:
            # Plain connection then STARTTLS (port 587)
            server = smtplib.SMTP(host, port, timeout=10)
            print(f"✓ Connected to {host}:{port}")
            
            if use_starttls:
                server.starttls(context=ssl.create_default_context())
                print("✓ STARTTLS enabled")
        
        # Login
        server.login(username, password)
        print("✓ Login successful")
        
        # Create test message
        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = username  # Send to self for testing
        msg['Subject'] = f"SMTP Test from Python - {host}:{port}"
        
        body = f"""This is a test email sent via direct SMTP connection.
        
Server: {host}:{port}
SSL: {use_ssl}
STARTTLS: {use_starttls}

If you receive this, SMTP configuration is working correctly!
"""
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server.send_message(msg)
        print("✓ Test email sent successfully!")
        
        server.quit()
        print("✓ Connection closed cleanly")
        return True
        
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {e}")
        return False

def main():
    print("=" * 60)
    print("Direct SMTP Connection Test")
    print("=" * 60)
    
    # Amazon SES credentials
    username = "iharvey@agentmail.to"
    password = "am_us_cd05b848539e62a8f8399ebdda986586e461a17747f560654aead253d80f3a99"
    
    # Test different configurations
    print("\n1. Testing Amazon SES with SSL (port 465)...")
    test_smtp_connection("email-smtp.us-east-1.amazonaws.com", 465, 
                        username, password, use_ssl=True)
    
    print("\n2. Testing Amazon SES with STARTTLS (port 587)...")
    test_smtp_connection("email-smtp.us-east-1.amazonaws.com", 587,
                        username, password, use_ssl=False, use_starttls=True)
    
    print("\n3. Testing smtp.agentmail.to with SSL (port 465)...")
    test_smtp_connection("smtp.agentmail.to", 465,
                        username, password, use_ssl=True)
    
    print("\n4. Testing smtp.agentmail.to with STARTTLS (port 587)...")
    test_smtp_connection("smtp.agentmail.to", 587,
                        username, password, use_ssl=False, use_starttls=True)
    
    print("\n" + "=" * 60)
    print("Note: Amazon SES requires proper authentication.")
    print("The provided credentials might be for IMAP only, not SMTP.")
    print("AgentMail might have separate SMTP credentials.")

if __name__ == "__main__":
    main()