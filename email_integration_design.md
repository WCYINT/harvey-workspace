# Email Integration Design for Self-Improving-Agent

## Overview
Integrate the `iharvey@agentmail.to` email account with the self-improving-agent skill to enable bidirectional communication for learning, feedback, and reporting.

## Goals
1. **Receive feedback**: Process user emails to create learning entries
2. **Send notifications**: Alert users about important learnings/errors
3. **Periodic reports**: Send daily/weekly learning summaries
4. **Self-evolution**: Use email as a channel for continuous improvement

## Architecture

### Components
1. **Email Client Module** (`email_client.py`)
   - Uses `himalaya` CLI or direct SMTP/IMAP libraries
   - Manages connections to `iharvey@agentmail.to`
   - Handles authentication with provided token

2. **Notification Manager** (`notify.py`)
   - Monitors `.learnings/` directory for new entries
   - Sends email notifications for high-priority items
   - Configurable thresholds (priority >= high, errors, etc.)

3. **Feedback Processor** (`feedback.py`)
   - Polls inbox for user emails
   - Parses email content to extract learning data
   - Creates entries in `.learnings/` based on user feedback
   - Supports structured formats (templates) and free-form

4. **Report Generator** (`reports.py`)
   - Generates daily/weekly learning summaries
   - Formats markdown reports as email content
   - Sends scheduled reports

5. **Configuration** (`email_config.py`)
   - Email account settings
   - Notification preferences
   - Polling intervals
   - Filter rules

## Integration Points with Self-Improving-Agent

### 1. Hook Extension
Extend existing hooks to trigger email notifications:
- `PostLearningLogged` → Send notification if priority >= high
- `PostErrorLogged` → Send error alert
- `DailyHeartbeat` → Send daily report

### 2. Learning Entry Enhancement
Add email metadata to learning entries:
```markdown
### Metadata
- Source: email_feedback | email_report | ...
- EmailThread: message-id
- ResponseRequired: true/false
```

### 3. Feedback Processing Pipeline
```
User Email → Parse → Classify → Create Learning → Send Acknowledgment
```

## Email Formats

### 1. User Feedback Email Template
```
Subject: Feedback: [Brief description]

Category: correction|error|feature|knowledge
Priority: low|medium|high|critical
Area: frontend|backend|infra|tests|docs|config

[Detailed description of the issue/suggestion]

[Optional: Suggested fix or additional context]
```

### 2. Notification Email Template
```
Subject: [LRN-20250306-001] New learning logged: [Summary]

A new learning has been logged in the self-improvement system:

**Learning ID**: LRN-20250306-001
**Category**: [category]
**Priority**: [priority]
**Area**: [area]

**Summary**: [one-line description]

**Details**: [full context]

View in workspace: .learnings/LEARNINGS.md
```

### 3. Daily Report Template
```
Subject: Self-Improvement Daily Report - YYYY-MM-DD

## Summary
- New learnings: X
- Errors logged: Y
- Feature requests: Z

## High Priority Items
1. [Learning 1]
2. [Error 1]

## Resolved Today
- [Learning resolved]

## Pending Review
- [Items needing attention]

Full details: .learnings/
```

## Implementation Plan

### Phase 1: Basic Email Testing & Configuration
- ✅ Test IMAP/SMTP connectivity for agentmail.to
- ✅ Update himalaya configuration
- ✅ Verify send/receive capabilities
- Create backup configuration management

### Phase 2: Notification System
- Add email notification to self-improving-agent skill
- Create notification templates
- Implement priority filtering
- Test end-to-end notification flow

### Phase 3: Feedback Processing
- Implement inbox polling
- Create email parsing logic
- Integrate with learning creation
- Add acknowledgment emails

### Phase 4: Scheduled Reports
- Implement daily report generation
- Add scheduling mechanism (cron/heartbeat)
- Create report templates
- Test report delivery

### Phase 5: Advanced Features
- Email threading for conversations
- Automated response suggestions
- Learning validation via email confirmation
- Integration with other skills (proactive-agent, etc.)

## Configuration

### Email Account Settings (himalaya format)
```toml
[accounts.iharvey]
email = "iharvey@agentmail.to"
display-name = "Havery AI Assistant"

[accounts.iharvey.imap]
host = "imap.agentmail.to"
port = 993
tls = true
login = "iharvey@agentmail.to"
password = "[token]"

[accounts.iharvey.smtp]
host = "smtp.agentmail.to"  # or Amazon SES
port = 587
tls = true
login = "iharvey@agentmail.to"
password = "[token]"
```

### Notification Settings
```yaml
notifications:
  enabled: true
  levels:
    - error
    - critical
    - high
  methods:
    email: true
  schedule:
    daily_report: "09:00"
    weekly_summary: "Monday 09:00"
```

## Testing Strategy

1. **Connectivity Tests**
   - IMAP login and folder listing
   - SMTP send test email
   - Round-trip (send to self, receive)

2. **Notification Tests**
   - Trigger learning log → verify email sent
   - Priority filtering works correctly
   - Template rendering

3. **Feedback Tests**
   - Send structured feedback email → verify learning created
   - Send free-form email → verify parsing
   - Acknowledgment email sent back

4. **Report Tests**
   - Daily report generation
   - Content accuracy
   - Scheduling

## Security Considerations

1. **Token Protection**
   - Store credentials securely (encrypted config)
   - Never log credentials
   - Regular token rotation

2. **Email Validation**
   - Verify sender authenticity
   - Prevent spam processing
   - Rate limiting

3. **Data Privacy**
   - Don't include sensitive info in emails
   - Anonymize data in reports
   - User consent for notifications

## Open Questions

1. Should email integration be optional or always-on?
2. How to handle email threading for ongoing conversations?
3. What's the fallback if email service is unavailable?
4. How to integrate with OpenClaw's existing notification system?
5. Should there be a webhook alternative to email polling?

## Success Metrics

1. **User Engagement**
   - Number of feedback emails processed
   - Response time to user feedback
   - User satisfaction with email interactions

2. **System Effectiveness**
   - Learning creation rate from email
   - Error resolution time with email notifications
   - Report delivery reliability

3. **Technical Performance**
   - Email processing latency
   - System uptime
   - Error rate in email operations