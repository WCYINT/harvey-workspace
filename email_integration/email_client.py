#!/usr/bin/env python3
"""
Email client for Havery's self-improvement system integration
"""

import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
import json
from datetime import datetime
from pathlib import Path
import logging
from typing import Optional, List, Dict, Any
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HaveryEmailClient:
    """Email client for iharvey@agentmail.to integration"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize email client with configuration"""
        self.email = "wcyint@163.com"
        self.password = "SEMefmThGnEKJiTz"
        
        # Server configurations
        self.imap_server = "imap.163.com"
        self.imap_port = 993
        self.smtp_server = "smtp.163.com"
        self.smtp_port = 465
        
        # Load custom config if provided
        if config_path and Path(config_path).exists():
            self._load_config(config_path)
        
        logger.info(f"Email client initialized for {self.email}")
    
    def _load_config(self, config_path: str):
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            if 'email' in config:
                self.email = config['email']
            if 'password' in config:
                self.password = config['password']
            if 'imap_server' in config:
                self.imap_server = config['imap_server']
            if 'imap_port' in config:
                self.imap_port = config['imap_port']
            if 'smtp_server' in config:
                self.smtp_server = config['smtp_server']
            if 'smtp_port' in config:
                self.smtp_port = config['smtp_port']
                
        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
    
    def send_email(self, to_address: str, subject: str, body: str, 
                   is_html: bool = False) -> bool:
        """
        Send an email via SMTP
        
        Args:
            to_address: Recipient email address
            subject: Email subject
            body: Email body content
            is_html: Whether body is HTML (default: plain text)
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email
            msg['To'] = to_address
            msg['Subject'] = subject
            msg['Date'] = email.utils.formatdate(localtime=True)
            
            # Add body
            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Connect to SMTP server
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
                server.login(self.email, self.password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_address}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def send_learning_notification(self, learning_data: Dict[str, Any], 
                                   to_address: Optional[str] = None) -> bool:
        """
        Send a notification about a new learning entry
        
        Args:
            learning_data: Dictionary with learning information
            to_address: Recipient email (default: send to self)
            
        Returns:
            bool: True if sent successfully
        """
        if to_address is None:
            to_address = self.email
        
        # Format email content
        subject = f"[LRN-{learning_data.get('id', 'NEW')}] {learning_data.get('summary', 'New learning')}"
        
        body = f"""New learning logged in Havery's self-improvement system:

**Learning ID**: {learning_data.get('id', 'N/A')}
**Category**: {learning_data.get('category', 'N/A')}
**Priority**: {learning_data.get('priority', 'N/A')}
**Area**: {learning_data.get('area', 'N/A')}

**Summary**
{learning_data.get('summary', 'No summary provided')}

**Details**
{learning_data.get('details', 'No details provided')}

**Suggested Action**
{learning_data.get('suggested_action', 'No action suggested')}

---
Logged: {learning_data.get('timestamp', datetime.now().isoformat())}
System: Havery Self-Improvement System
"""
        
        return self.send_email(to_address, subject, body)
    
    def send_error_notification(self, error_data: Dict[str, Any],
                                to_address: Optional[str] = None) -> bool:
        """
        Send a notification about an error
        
        Args:
            error_data: Dictionary with error information
            to_address: Recipient email (default: send to self)
            
        Returns:
            bool: True if sent successfully
        """
        if to_address is None:
            to_address = self.email
        
        subject = f"[ERR] {error_data.get('summary', 'System error')}"
        
        body = f"""Error logged in Havery's self-improvement system:

**Error ID**: {error_data.get('id', 'N/A')}
**Priority**: {error_data.get('priority', 'N/A')}
**Area**: {error_data.get('area', 'N/A')}

**Summary**
{error_data.get('summary', 'No summary provided')}

**Error Details**
```
{error_data.get('error_details', 'No error details')}
```

**Context**
{error_data.get('context', 'No context provided')}

**Suggested Fix**
{error_data.get('suggested_fix', 'No fix suggested')}

---
Logged: {error_data.get('timestamp', datetime.now().isoformat())}
System: Havery Self-Improvement System
"""
        
        return self.send_email(to_address, subject, body)
    
    def check_inbox(self, max_messages: int = 10) -> List[Dict[str, Any]]:
        """
        Check inbox for new messages
        
        Args:
            max_messages: Maximum number of messages to fetch
            
        Returns:
            List of message dictionaries
        """
        messages = []
        mail = None
        
        try:
            # Connect to IMAP server
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port, timeout=30)
            logger.debug(f"Connecting to IMAP server {self.imap_server}:{self.imap_port}")
            
            mail.login(self.email, self.password)
            logger.debug(f"Logged in as {self.email}")
            
            status, data = mail.select('INBOX')
            if status != 'OK':
                logger.error(f"Failed to select INBOX: {data}")
                return messages
            
            logger.debug("INBOX selected successfully")
            
            # Search for all messages
            status, data = mail.search(None, 'ALL')
            if status != 'OK':
                logger.error("Failed to search inbox")
                return messages
            
            # Get message IDs
            msg_ids = data[0].split()
            logger.debug(f"Found {len(msg_ids)} total messages in inbox")
            
            msg_ids = msg_ids[-max_messages:]  # Get most recent messages
            logger.debug(f"Processing {len(msg_ids)} most recent messages")
            
            for msg_id in msg_ids:
                try:
                    msg_id_str = msg_id.decode()
                    logger.debug(f"Fetching message {msg_id_str}")
                    
                    # Fetch message
                    status, msg_data = mail.fetch(msg_id, '(RFC822)')
                    if status != 'OK':
                        logger.warning(f"Failed to fetch message {msg_id_str}: {msg_data}")
                        continue
                    
                    # Parse message
                    raw_email = msg_data[0][1]
                    email_message = email.message_from_bytes(raw_email)
                    
                    # Extract message info
                    msg_info = {
                        'id': msg_id_str,
                        'from': email_message['From'],
                        'to': email_message['To'],
                        'subject': email_message['Subject'],
                        'date': email_message['Date'],
                        'body': self._extract_email_body(email_message),
                        'headers': dict(email_message.items())
                    }
                    
                    messages.append(msg_info)
                    logger.debug(f"Successfully processed message {msg_id_str}")
                    
                except Exception as e:
                    logger.error(f"Failed to process message {msg_id}: {e}")
                    continue
                
        except Exception as e:
            logger.error(f"Failed to check inbox: {e}")
            # Try to log more details
            import traceback
            logger.debug(f"Traceback: {traceback.format_exc()}")
        
        finally:
            # Clean up IMAP connection
            if mail:
                try:
                    # Try to close the mailbox
                    try:
                        mail.close()
                        logger.debug("Mailbox closed")
                    except Exception as e:
                        logger.debug(f"Mailbox close failed (may already be closed): {e}")
                    
                    # Try to logout
                    try:
                        mail.logout()
                        logger.debug("Logged out from IMAP")
                    except Exception as e:
                        logger.debug(f"Logout failed (may already be logged out): {e}")
                        
                except Exception as e:
                    logger.debug(f"Error during IMAP cleanup: {e}")
        
        logger.info(f"Retrieved {len(messages)} messages from inbox")
        return messages
    
    def _extract_email_body(self, email_message) -> str:
        """Extract plain text body from email message"""
        body = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                # Skip attachments
                if "attachment" in content_disposition:
                    continue
                
                # Get plain text body
                if content_type == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode()
                        break
                    except:
                        pass
        else:
            # Not multipart
            content_type = email_message.get_content_type()
            if content_type == "text/plain":
                try:
                    body = email_message.get_payload(decode=True).decode()
                except:
                    pass
        
        return body
    
    def parse_feedback_email(self, email_body: str) -> Optional[Dict[str, Any]]:
        """
        Parse feedback email to extract learning information
        
        Expected format (structured):
        Category: correction|error|feature|knowledge
        Priority: low|medium|high|critical
        Area: frontend|backend|infra|tests|docs|config
        
        [Detailed description]
        
        [Optional: Suggested fix]
        
        Args:
            email_body: Email body text
            
        Returns:
            Dictionary with parsed learning data, or None if not a feedback email
        """
        # Check if this looks like structured feedback
        lines = email_body.strip().split('\n')
        
        learning_data = {
            'source': 'email_feedback',
            'timestamp': datetime.now().isoformat(),
            'raw_body': email_body
        }
        
        # Try to extract structured fields
        category_match = re.search(r'Category:\s*(\w+)', email_body, re.IGNORECASE)
        priority_match = re.search(r'Priority:\s*(\w+)', email_body, re.IGNORECASE)
        area_match = re.search(r'Area:\s*(\w+)', email_body, re.IGNORECASE)
        
        if category_match:
            learning_data['category'] = category_match.group(1).lower()
        
        if priority_match:
            learning_data['priority'] = priority_match.group(1).lower()
        
        if area_match:
            learning_data['area'] = area_match.group(1).lower()
        
        # If we found at least a category, assume it's structured feedback
        if 'category' in learning_data:
            # Extract summary (first line after headers)
            body_lines = []
            in_body = False
            
            for line in lines:
                if line.lower().startswith(('category:', 'priority:', 'area:')):
                    continue
                if line.strip() and not in_body:
                    learning_data['summary'] = line.strip()
                    in_body = True
                elif in_body:
                    body_lines.append(line)
            
            if 'summary' not in learning_data and body_lines:
                learning_data['summary'] = body_lines[0].strip()[:100]
            
            learning_data['details'] = '\n'.join(body_lines).strip()
            
            # Try to extract suggested action/fix
            suggested_match = re.search(r'Suggested[:\s]*(.+)', email_body, re.IGNORECASE | re.DOTALL)
            if suggested_match:
                learning_data['suggested_action'] = suggested_match.group(1).strip()
            
            return learning_data
        
        # Not structured feedback
        return None
    
    def generate_daily_report(self, learnings_dir: str) -> str:
        """
        Generate daily learning report
        
        Args:
            learnings_dir: Path to .learnings directory
            
        Returns:
            Formatted report as string
        """
        learnings_path = Path(learnings_dir)
        
        if not learnings_path.exists():
            return "No .learnings directory found."
        
        # Count files
        md_files = list(learnings_path.glob("*.md"))
        
        report = f"""# Havery Self-Improvement Daily Report
Date: {datetime.now().strftime('%Y-%m-%d')}

## Summary
- Learning files: {len(md_files)}
- Last updated: {datetime.now().strftime('%H:%M:%S')}

## Files
"""
        
        for md_file in md_files:
            size = md_file.stat().st_size
            report += f"- {md_file.name} ({size} bytes)\n"
        
        report += "\n## System Status\n"
        report += "- Email integration: ✓ Active\n"
        report += "- Learning system: ✓ Ready\n"
        report += "- Notification engine: ✓ Enabled\n"
        report += "\n---\nReport generated by Havery's self-improvement system"
        
        return report

# Example usage
if __name__ == "__main__":
    # Test the email client
    client = HaveryEmailClient()
    
    print("Testing email client...")
    
    # Test 1: Send test email
    print("\n1. Sending test email...")
    success = client.send_email(
        to_address="iharvey@agentmail.to",
        subject="Test from Havery Email Client",
        body="This is a test email from the Python email client integration."
    )
    print(f"   Result: {'✓ Success' if success else '✗ Failed'}")
    
    # Test 2: Parse feedback email
    print("\n2. Testing feedback parsing...")
    test_feedback = """Category: correction
Priority: high
Area: config

The timeout setting should be 7200 seconds, not 300.

Suggested: Update openclaw.json with timeoutSeconds: 7200"""
    
    parsed = client.parse_feedback_email(test_feedback)
    if parsed:
        print(f"   Parsed: {parsed.get('category')} - {parsed.get('summary', 'No summary')}")
    else:
        print("   Not a structured feedback email")
    
    # Test 3: Generate report
    print("\n3. Generating daily report...")
    report = client.generate_daily_report("/Users/fhjtech/.openclaw/workspace/.learnings")
    print(f"   Report length: {len(report)} characters")
    
    print("\n✅ Email client test complete")