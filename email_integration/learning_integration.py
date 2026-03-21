#!/usr/bin/env python3
"""
Integration between email system and self-improving-agent
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
from email_client import HaveryEmailClient
import json
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Skills Integration
SKILLS_TRACKING_FILE = "/Users/fhjtech/.openclaw/workspace/.learnings/skills_usage.json"

SKILL_TRIGGERS = {
    "academic": ["academic", "paper", "research", "thesis", "MBA", "arxiv"],
    "business": ["business", "market", "data analysis", "decision", "resume"],
    "search": ["search", "news", "tavily", "exa", "tldr", "RSS"],
    "dev": ["github", "pdf", "code", "browser automation"],
    "productivity": ["brainstorm", "daily", "productivity", "free model"],
    "improvement": ["improve", "learn", "evolve", "feedback"]
}

class LearningEmailIntegrator:
    """
    Integrates email system with self-improving-agent learning files
    """
    
    def __init__(self, learnings_dir: Optional[str] = None):
        """Initialize integrator with paths"""
        if learnings_dir is None:
            self.learnings_dir = Path("/Users/fhjtech/.openclaw/workspace/.learnings")
        else:
            self.learnings_dir = Path(learnings_dir)
        
        self.email_client = HaveryEmailClient()
        
        # Ensure directories exist
        self.learnings_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"LearningEmailIntegrator initialized with directory: {self.learnings_dir}")
    
    def record_skill_usage(self, skill_name: str, context: str = ""):
        """Record skill usage for learning and optimization"""
        try:
            data = self._load_skills_data()
            
            if skill_name not in data["skills"]:
                data["skills"][skill_name] = {"count": 0, "first_used": None, "contexts": []}
            
            data["skills"][skill_name]["count"] += 1
            data["skills"][skill_name]["last_used"] = datetime.now().isoformat()
            
            if not data["skills"][skill_name]["first_used"]:
                data["skills"][skill_name]["first_used"] = datetime.now().isoformat()
            
            if context:
                data["skills"][skill_name]["contexts"].append(context[:200])  # Truncate long contexts
            
            # Track category usage
            for category, triggers in SKILL_TRIGGERS.items():
                if any(t.lower() in skill_name.lower() for t in triggers):
                    data["categories"][category] = data["categories"].get(category, 0) + 1
            
            data["total_uses"] += 1
            data["last_update"] = datetime.now().isoformat()
            
            self._save_skills_data(data)
            logger.info(f"Recorded skill usage: {skill_name}")
        except Exception as e:
            logger.error(f"Failed to record skill usage: {e}")
    
    def _load_skills_data(self) -> dict:
        """Load skills usage data"""
        if os.path.exists(SKILLS_TRACKING_FILE):
            with open(SKILLS_TRACKING_FILE, 'r') as f:
                return json.load(f)
        return {"skills": {}, "categories": {}, "total_uses": 0, "last_update": None}
    
    def _save_skills_data(self, data: dict):
        """Save skills usage data"""
        os.makedirs(os.path.dirname(SKILLS_TRACKING_FILE), exist_ok=True)
        with open(SKILLS_TRACKING_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_skill_stats(self) -> dict:
        """Get skill usage statistics"""
        return self._load_skills_data()
    
    def create_learning_from_email(self, email_data: Dict[str, Any]) -> Optional[str]:
        """
        Create a learning entry from email feedback
        
        Args:
            email_data: Parsed email data from parse_feedback_email()
            
        Returns:
            Path to created learning file, or None if failed
        """
        try:
            # Generate learning ID
            date_str = datetime.now().strftime("%Y%m%d")
            learning_id = f"LRN-{date_str}-{self._generate_suffix()}"
            
            # Determine which file to write to
            category = email_data.get('category', 'other')
            file_map = {
                'correction': 'LEARNINGS.md',
                'error': 'ERRORS.md', 
                'feature': 'FEATURE_REQUESTS.md',
                'knowledge': 'LEARNINGS.md'
            }
            
            filename = file_map.get(category, 'LEARNINGS.md')
            filepath = self.learnings_dir / filename
            
            # Create learning entry
            entry = self._format_learning_entry(learning_id, email_data)
            
            # Append to file
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(entry)
            
            logger.info(f"Created learning entry {learning_id} in {filename}")
            
            # Send acknowledgment email
            self._send_acknowledgment(email_data, learning_id)
            
            # Send notification if high priority
            if email_data.get('priority') in ['high', 'critical']:
                self.email_client.send_learning_notification({
                    'id': learning_id,
                    'category': category,
                    'priority': email_data.get('priority', 'medium'),
                    'area': email_data.get('area', 'other'),
                    'summary': email_data.get('summary', 'No summary'),
                    'details': email_data.get('details', ''),
                    'suggested_action': email_data.get('suggested_action', ''),
                    'timestamp': datetime.now().isoformat()
                })
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Failed to create learning from email: {e}")
            return None
    
    def _format_learning_entry(self, learning_id: str, data: Dict[str, Any]) -> str:
        """Format learning entry in markdown"""
        timestamp = datetime.now().isoformat()
        category = data.get('category', 'other')
        priority = data.get('priority', 'medium')
        area = data.get('area', 'other')
        summary = data.get('summary', 'No summary').replace('\n', ' ')
        details = data.get('details', 'No details provided')
        suggested = data.get('suggested_action', 'No suggested action')
        
        entry = f"""## [{learning_id}] {category}

**Logged**: {timestamp}
**Priority**: {priority}
**Status**: pending
**Area**: {area}

### Summary
{summary}

### Details
{details}

### Suggested Action
{suggested}

### Metadata
- Source: email_feedback
- EmailThread: N/A
- ResponseRequired: false
- Tags: email_integration
- See Also: 

---
"""
        return entry
    
    def _generate_suffix(self) -> str:
        """Generate 3-character suffix for learning ID"""
        import random
        import string
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
    
    def _send_acknowledgment(self, email_data: Dict[str, Any], learning_id: str):
        """Send acknowledgment email for received feedback"""
        subject = f"Feedback received: {learning_id}"
        
        body = f"""Thank you for your feedback to Havery's self-improvement system.

Your feedback has been logged as: {learning_id}
Category: {email_data.get('category', 'N/A')}
Priority: {email_data.get('priority', 'medium')}

**Summary**: {email_data.get('summary', 'No summary')}

The learning entry has been added to the system and will be reviewed.
You can find it in: {self.learnings_dir}/{self._get_filename_for_category(email_data.get('category'))}

---
This is an automated response from Havery's self-improvement system.
"""
        
        # Try to get sender from original email
        sender = email_data.get('from', self.email_client.email)
        
        # Send acknowledgment
        self.email_client.send_email(
            to_address=sender,
            subject=subject,
            body=body
        )
    
    def _get_filename_for_category(self, category: str) -> str:
        """Get filename for category"""
        mapping = {
            'correction': 'LEARNINGS.md',
            'error': 'ERRORS.md',
            'feature': 'FEATURE_REQUESTS.md',
            'knowledge': 'LEARNINGS.md'
        }
        return mapping.get(category, 'LEARNINGS.md')
    
    def process_inbox_feedback(self, max_messages: int = 20) -> List[str]:
        """
        Process inbox for feedback emails and create learning entries
        
        Args:
            max_messages: Maximum messages to process
            
        Returns:
            List of created learning IDs
        """
        # Rate limit: only run at 9am or 9pm to avoid IP bans from 163邮箱
        current_hour = datetime.now().hour
        if current_hour not in (9, 21):
            logger.info(f"Rate limit: skipping inbox check (hour={current_hour}, only runs at 9 or 21)")
            return []
        
        created_learnings = []
        
        try:
            # Get messages from inbox
            messages = self.email_client.check_inbox(max_messages=max_messages)
            
            for msg in messages:
                try:
                    # Parse feedback
                    feedback_data = self.email_client.parse_feedback_email(msg['body'])
                    
                    if feedback_data:
                        # Add email metadata
                        feedback_data['from'] = msg['from']
                        feedback_data['subject'] = msg['subject']
                        feedback_data['date'] = msg['date']
                        
                        # Create learning entry
                        filepath = self.create_learning_from_email(feedback_data)
                        
                        if filepath:
                            learning_id = re.search(r'\[(LRN-[^]]+)\]', Path(filepath).read_text())
                            if learning_id:
                                created_learnings.append(learning_id.group(1))
                                logger.info(f"Created learning from email: {learning_id.group(1)}")
                    
                except Exception as e:
                    logger.error(f"Failed to process message {msg.get('id')}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Failed to process inbox: {e}")
        
        logger.info(f"Processed inbox, created {len(created_learnings)} learning entries")
        return created_learnings
    
    def send_daily_report(self, recipient: Optional[str] = None) -> bool:
        """
        Send daily learning report via email
        
        Args:
            recipient: Email recipient (default: self)
            
        Returns:
            True if sent successfully
        """
        if recipient is None:
            recipient = self.email_client.email
        
        # Generate report
        report = self.email_client.generate_daily_report(str(self.learnings_dir))
        
        # Send email
        subject = f"Havery Self-Improvement Daily Report - {datetime.now().strftime('%Y-%m-%d')}"
        
        success = self.email_client.send_email(
            to_address=recipient,
            subject=subject,
            body=report
        )
        
        if success:
            logger.info(f"Daily report sent to {recipient}")
        else:
            logger.error(f"Failed to send daily report to {recipient}")
        
        return success
    
    def monitor_and_process(self, interval_minutes: int = 60):
        """
        Monitor inbox and process feedback periodically
        
        Args:
            interval_minutes: Check interval in minutes
        """
        import time
        
        logger.info(f"Starting email monitoring (interval: {interval_minutes} minutes)")
        
        try:
            while True:
                # Process inbox
                created = self.process_inbox_feedback()
                
                if created:
                    logger.info(f"Processed {len(created)} feedback emails")
                
                # Wait for next interval
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            logger.info("Email monitoring stopped")
        except Exception as e:
            logger.error(f"Email monitoring error: {e}")

# CLI interface
if __name__ == "__main__":
    import argparse
    import signal
    import sys
    
    # Set a timeout to prevent hanging
    def timeout_handler(signum, frame):
        print("TIMEOUT: Exiting after timeout")
        sys.exit(0)
    
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(60)  # 60 second timeout
    
    parser = argparse.ArgumentParser(description="Havery Email-Learning Integration")
    parser.add_argument('--action', choices=['process', 'report', 'test', 'monitor'], 
                       default='test', help='Action to perform')
    parser.add_argument('--recipient', help='Email recipient for reports')
    parser.add_argument('--interval', type=int, default=60, 
                       help='Monitoring interval in minutes (for monitor action)')
    
    args = parser.parse_args()
    
    integrator = LearningEmailIntegrator()
    
    if args.action == 'process':
        print("Processing inbox for feedback emails...")
        created = integrator.process_inbox_feedback()
        print(f"Created {len(created)} learning entries: {created}")
    
    elif args.action == 'report':
        print("Sending daily report...")
        success = integrator.send_daily_report(args.recipient)
        print(f"Report sent: {'✓ Success' if success else '✗ Failed'}")
    
    elif args.action == 'monitor':
        print(f"Starting email monitoring (interval: {args.interval} minutes)")
        print("Press Ctrl+C to stop")
        integrator.monitor_and_process(args.interval)
    
    elif args.action == 'test':
        print("Testing email-learning integration...")
        
        # Test creating learning from email
        test_email = {
            'category': 'correction',
            'priority': 'high',
            'area': 'config',
            'summary': 'Timeout should be 7200 seconds for long tasks',
            'details': 'User requested timeout increase from 300 to 7200 seconds for agent tasks.',
            'suggested_action': 'Update agents.defaults.timeoutSeconds in openclaw.json',
            'from': 'iharvey@agentmail.to',
            'subject': 'Feedback: Timeout configuration'
        }
        
        print("\n1. Testing learning creation from email...")
        filepath = integrator.create_learning_from_email(test_email)
        print(f"   Result: {'✓ Created' if filepath else '✗ Failed'}")
        
        # Test inbox processing
        print("\n2. Testing inbox processing...")
        created = integrator.process_inbox_feedback(max_messages=5)
        print(f"   Processed {len(created)} emails")
        
        # Test report generation
        print("\n3. Testing report generation...")
        report = integrator.email_client.generate_daily_report(str(integrator.learnings_dir))
        print(f"   Report length: {len(report)} characters")
        
        print("\n✅ Integration test complete")