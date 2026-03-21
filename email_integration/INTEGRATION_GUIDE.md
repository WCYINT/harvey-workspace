# Email Integration Guide for Self-Improving-Agent

## Overview
This guide explains how to integrate the email system with the self-improving-agent skill to enable bidirectional communication for learning, feedback, and reporting.

## Architecture

```
Email System ↔ Learning System
     ↓              ↓
  Feedback       Learning
   Emails        Entries
     ↓              ↓
  Parser        Generator
     ↓              ↓
  .learnings/   Notifications
     ↓              ↓
  Behavior       Reports
   Updates
```

## Components

### 1. Email Client (`email_client.py`)
- SMTP client for sending emails
- IMAP client for receiving emails
- Email parsing and formatting utilities

### 2. Learning Integrator (`learning_integration.py`)
- Creates learning entries from email feedback
- Sends notifications for high-priority learnings
- Processes inbox for feedback emails
- Generates and sends daily reports

### 3. Integration Hooks
- Periodic inbox monitoring
- Learning creation triggers
- Report scheduling

## Installation

### Step 1: Copy Integration Files
```bash
# Copy email integration to self-improving-agent directory
cp -r email_integration/ /Users/fhjtech/.openclaw/workspace/skills/self-improving-agent/
```

### Step 2: Update Skill Configuration
Add email integration configuration to the skill's SKILL.md or create a separate configuration file.

### Step 3: Configure Email Settings
Ensure `~/.config/himalaya/config.toml` contains correct SMTP/IMAP settings for `iharvey@agentmail.to`.

## Usage

### Manual Processing
```bash
# Process inbox for feedback emails
cd /Users/fhjtech/.openclaw/workspace/email_integration
python3 learning_integration.py --action process

# Send daily report
python3 learning_integration.py --action report --recipient your@email.com

# Test integration
python3 learning_integration.py --action test
```

### Automated Monitoring
```bash
# Start continuous monitoring (checks every 60 minutes)
python3 learning_integration.py --action monitor --interval 60
```

### Programmatic Usage
```python
from learning_integration import LearningEmailIntegrator

# Initialize integrator
integrator = LearningEmailIntegrator()

# Process inbox
created_learnings = integrator.process_inbox_feedback()

# Send report
integrator.send_daily_report("recipient@example.com")
```

## Integration with Self-Improving-Agent

### Option A: Hook-Based Integration
Add email processing hooks to the self-improving-agent skill:

1. **Post-Learning Hook**: Send notification when high-priority learning is logged
2. **Periodic Hook**: Check inbox and process feedback periodically
3. **Daily Report Hook**: Send daily summary report

### Option B: Standalone Service
Run email integration as a separate service/daemon that monitors the `.learnings/` directory and inbox.

### Option C: OpenClaw Cron Integration
Schedule email processing via OpenClaw cron jobs:
```json
{
  "cron": {
    "email_monitor": {
      "schedule": "*/30 * * * *",  // Every 30 minutes
      "command": "python3 /path/to/learning_integration.py --action process"
    },
    "daily_report": {
      "schedule": "0 9 * * *",  // Daily at 9 AM
      "command": "python3 /path/to/learning_integration.py --action report"
    }
  }
}
```

## Feedback Email Format

Users should send feedback emails in this structured format:

```
Category: correction|error|feature|knowledge
Priority: low|medium|high|critical
Area: frontend|backend|infra|tests|docs|config

[Detailed description of the issue/suggestion]

[Optional: Suggested fix or additional context]
```

### Example Feedback Email
```
Category: correction
Priority: high
Area: config

The timeout setting should be 7200 seconds, not 300 seconds for long-running tasks.

Suggested: Update agents.defaults.timeoutSeconds in openclaw.json to 7200
```

## Notification System

### Learning Notifications
- Sent when learning with priority ≥ "high" is created
- Includes learning ID, category, priority, and summary
- Sent to configured recipients (default: self)

### Error Notifications
- Sent when error entries are created
- Includes error details and suggested fix
- High-priority alerts for critical issues

### Daily Reports
- Summary of new learnings, errors, and feature requests
- System status overview
- Sent daily at configured time

## Configuration

### Email Settings
Configure in `~/.config/himalaya/config.toml`:
```toml
[accounts.iharvey]
email = "iharvey@agentmail.to"
display-name = "Havery AI Assistant"
default = true

[accounts.iharvey.imap]
host = "imap.agentmail.to"
port = 993
tls = true
login = "iharvey@agentmail.to"
password = "am_us_cd05b848539e62a8f8399ebdda986586e461a17747f560654aead253d80f3a99"

[accounts.iharvey.smtp]
host = "smtp.agentmail.to"
port = 465
tls = true
login = "iharvey@agentmail.to"
password = "am_us_cd05b848539e62a8f8399ebdda986586e461a17747f560654aead253d80f3a99"
```

### Integration Settings
Create `email_config.json`:
```json
{
  "monitoring": {
    "enabled": true,
    "interval_minutes": 60,
    "max_messages": 20
  },
  "notifications": {
    "enabled": true,
    "min_priority": "high",
    "recipients": ["iharvey@agentmail.to"]
  },
  "reports": {
    "enabled": true,
    "schedule": "09:00",
    "recipient": "iharvey@agentmail.to"
  },
  "learnings_dir": "/Users/fhjtech/.openclaw/workspace/.learnings"
}
```

## Testing

### Test Suite
```bash
# Test email sending
python3 test_smtp_direct.py

# Test integration
python3 learning_integration.py --action test

# Test with real email
python3 -c "from email_client import HaveryEmailClient; c = HaveryEmailClient(); c.send_email('iharvey@agentmail.to', 'Test', 'Test body')"
```

### Verification Steps
1. Send test email to `iharvey@agentmail.to`
2. Process inbox: `python3 learning_integration.py --action process`
3. Check `.learnings/` directory for new entries
4. Verify notification emails received

## Troubleshooting

### Common Issues

#### SMTP Connection Failed
- Verify SMTP server and port
- Check credentials
- Test with `test_smtp_direct.py`

#### IMAP Connection Failed
- Verify IMAP server and port
- Check credentials
- Ensure SSL/TLS settings correct

#### No Learning Created from Email
- Check email format matches structured template
- Verify email parsing logic
- Check file permissions in `.learnings/` directory

#### Notifications Not Sent
- Verify notification configuration
- Check priority thresholds
- Test email sending separately

### Logging
Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Security Considerations

### Credential Management
- Store email credentials securely
- Use environment variables for sensitive data
- Consider credential encryption

### Email Validation
- Validate sender addresses
- Implement spam filtering
- Rate limit processing

### Data Privacy
- Don't include sensitive information in notifications
- Anonymize data in reports
- Secure storage of email content

## Future Enhancements

### Planned Features
1. **Email Threading**: Track conversations and responses
2. **Advanced Parsing**: Natural language processing for unstructured feedback
3. **Web Interface**: Web dashboard for learning management
4. **Multi-language Support**: Support for feedback in different languages
5. **Integration with Other Skills**: Connect with proactive-agent, research skills, etc.

### Integration Points
- OpenClaw cron system for scheduling
- OpenClaw hooks for event-driven processing
- Webhook support for external systems
- API for programmatic access

## Support

For issues or questions:
1. Check logs in `/tmp/havery_email.log`
2. Test individual components
3. Review configuration files
4. Contact system administrator

## Changelog

### v1.0.0 (Initial Release)
- Basic email sending/receiving
- Learning creation from structured feedback
- Notification system for high-priority items
- Daily report generation
- Integration with self-improving-agent