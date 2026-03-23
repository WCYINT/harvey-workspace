# Errors

Command failures, exceptions, and unexpected behavior.

**Areas**: frontend | backend | infra | tests | docs | config
**Statuses**: pending | in_progress | resolved | wont_fix

---

## [ERR-20260322-DTC] infra

**Logged**: 2026-03-22T22:11:00+08:00
**Status**: resolved
**Resolution**: Removed custom-api-deepseek-com/deepseek-chat and deepseek-reasoner from gateway fallback chain (2026-03-22T14:32+08:00). DeepSeek API key out of credits was causing ~20s cascading delays per failure. Gateway restarted.
**Area**: infra

### Summary
Duplicate tool_call id "read32" — MiniMax API error 2013, blocking proactive cron

### Details
Error `"LLM request rejected: invalid params, duplicate tool_call id: read32 (2013)"` occurred 4+ times (21:59, 22:01, 22:05, 22:12 UTC+8) across different runIds and models. Same tool_call ID "read32" reused across retries → gateway session state persists tool_call IDs across LLM call retries.

### Impact
Hourly proactive cron jobs failing. Gateway in draining state.

### Prevention
Cannot fix gateway session state from workspace. Ensure each cron run uses a fresh session.

### Metadata
- See Also: gateway.err.log lines ~70402, 70431, 70505, 70611

---


## 2026-03-24 06:00 - 163 SMTP认证失败
**问题**: daily_skills_summary.py 和 email_integration 发送邮件均失败
**错误**: `(535, b'Error: authentication failed')`
**排查**:
- 授权码 NDdE6mZyTMifExXL 在 TOOLS.md 中记录
- 尝试 SSL(465) 和 TLS(587) 均失败
- 可能原因: 163授权码过期或需重新生成
**建议**: James需要到163邮箱设置重新生成SMTP授权码
