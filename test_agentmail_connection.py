#!/usr/bin/env python3
"""
Test connection to agentmail.to email service
"""

import socket
import ssl
import sys

def test_port(host, port, description):
    """Test if a TCP port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            print(f"✓ {description}: {host}:{port} is OPEN")
            return True
        else:
            print(f"✗ {description}: {host}:{port} is CLOSED (error: {result})")
            return False
    except Exception as e:
        print(f"✗ {description}: {host}:{port} - ERROR: {e}")
        return False

def test_imap_ssl(host, port):
    """Test IMAP SSL connection"""
    try:
        context = ssl.create_default_context()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        ssl_sock = context.wrap_socket(sock, server_hostname=host)
        ssl_sock.connect((host, port))
        
        # Read banner
        banner = ssl_sock.recv(1024)
        print(f"✓ IMAP SSL connection successful to {host}:{port}")
        print(f"  Banner: {banner[:100].decode('utf-8', errors='ignore')}")
        ssl_sock.close()
        return True
    except Exception as e:
        print(f"✗ IMAP SSL connection failed: {e}")
        return False

def test_smtp_starttls(host, port):
    """Test SMTP STARTTLS connection"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((host, port))
        
        # Read SMTP banner
        banner = sock.recv(1024)
        print(f"✓ SMTP connection to {host}:{port}")
        print(f"  Banner: {banner[:100].decode('utf-8', errors='ignore')}")
        
        # Send EHLO
        sock.send(b"EHLO test.local\r\n")
        response = sock.recv(1024)
        print(f"  EHLO response: {response[:200].decode('utf-8', errors='ignore')}")
        
        sock.close()
        return True
    except Exception as e:
        print(f"✗ SMTP connection failed: {e}")
        return False

def main():
    print("Testing agentmail.to email service connections...")
    print("=" * 60)
    
    # Test DNS resolution
    import subprocess
    try:
        result = subprocess.run(["dig", "+short", "imap.agentmail.to"], 
                              capture_output=True, text=True)
        imap_ips = result.stdout.strip().split('\n')
        print(f"imap.agentmail.to resolves to: {imap_ips}")
    except:
        print("Could not resolve imap.agentmail.to")
    
    try:
        result = subprocess.run(["dig", "+short", "smtp.agentmail.to"], 
                              capture_output=True, text=True)
        smtp_ips = result.stdout.strip().split('\n')
        print(f"smtp.agentmail.to resolves to: {smtp_ips}")
    except:
        print("Could not resolve smtp.agentmail.to")
    
    print("=" * 60)
    
    # Test ports
    test_port("imap.agentmail.to", 993, "IMAP SSL")
    test_port("imap.agentmail.to", 143, "IMAP plain")
    test_port("smtp.agentmail.to", 465, "SMTP SSL")
    test_port("smtp.agentmail.to", 587, "SMTP STARTTLS")
    test_port("smtp.agentmail.to", 25, "SMTP plain")
    
    print("=" * 60)
    
    # Test IMAP SSL
    test_imap_ssl("imap.agentmail.to", 993)
    
    print("=" * 60)
    
    # Test SMTP
    test_smtp_starttls("smtp.agentmail.to", 587)
    
    print("=" * 60)
    print("Testing Amazon SES endpoints (MX record shows Amazon SES)...")
    
    test_port("email-smtp.us-east-1.amazonaws.com", 587, "Amazon SES SMTP STARTTLS")
    test_port("email-smtp.us-east-1.amazonaws.com", 465, "Amazon SES SMTP SSL")
    test_port("email-smtp.us-east-1.amazonaws.com", 25, "Amazon SES SMTP plain")
    
    print("=" * 60)
    print("Note: AgentMail appears to be using Amazon SES for outbound email.")
    print("MX record points to: inbound-smtp.us-east-1.amazonaws.com")
    print("This suggests inbound email goes to Amazon SES, but IMAP might be separate.")

if __name__ == "__main__":
    main()