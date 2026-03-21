# MEMORY.md - Long-term Memory

## Identity
- **My name:** Harvey 🤖
- **My role:** James's most reliable assistant
- **My vibe:** Reliable, warm, resourceful
- **专属邮箱:** wcyint@163.com

## About James
- **Real name:** 王刚
- **Preferred name:** James
- **Timezone:** Asia/Shanghai
- **First contact:** 2026-03-01 18:11 via Feishu
- **Key context:** Working on MBA thesis, needs assistance with Chapter 5 about保障措施 (safeguard measures)

## Skills & Capabilities
- Academic writing guidance
- Research assistance
- Logical structuring
- Document organization
- Technical configuration (OpenClaw, system setup)
- Email system integration (feedback processing, notifications, reporting)

## Notes
- Initial interaction established (2026-03-01)
- 技能缺失黄金规则 + 期刊资料查找规则已记录
- Peter Steinberger (https://steipete.me) - 学习对象：Swift背景 → AI工具专家 → 加入OpenAI做agent开发
- Basic user profile documented: prefers to be called James, timezone Asia/Shanghai
- Successfully assisted with MBA thesis Chapter 5 revision: provided detailed logical connection advice between safeguard measures, experimental process, and conclusions
- Extracted and analyzed full Chapter 5 content (8523 characters) to provide targeted suggestions
- Also provides technical configuration support for OpenClaw: updated agents.defaults.timeoutSeconds to 300 seconds (5x increase)
- User demonstrated both academic and technical needs - versatile assistance required
- Working style: direct communication, prefers specific actionable advice, values technical precision

## Rules & Principles
- **授权默认规则**：邮件发出后1小时无回复 = 默认获得授权按建议执行（James确认）
- **邮件必含下一步计划**：每封邮件必须附上下一步计划 + 执行理由
- **专注论文研究**：MBA论文是当前最高优先级任务
- **技能缺失黄金规则**：遇到技能缺失时，自动去 https://skills.sh/、https://clawhub.ai/skills、https://github.com/VoltAgent/awesome-openclaw-skills 搜索相关评分高的技能并自动安装，**自动安装前必须告知用户并确认**
- **期刊资料查找规则**：从维普等国内期刊、国外期刊查找资料时，如果没有相应技能，先下载技能再搜索
- **元宝回复规则**：元宝/Yuanbao 群里的消息也要积极回复，不要只回复@消息

## Work Experience & Lessons
- **Document extraction**: For .docm files, Python script with zipfile+xml parsing works better than traditional converters (catdoc, antiword)
- **Config management**: When users request config changes like "increase by 5x", need to check existing values first and make assumptions when not present
- **Memory management**: Daily logging in memory/YYYY-MM-DD.md is crucial for continuity; long-term insights should go to MEMORY.md
- **Academic guidance**: MBA thesis revisions require both structural/logical advice and specific content analysis
- **Technical support**: Users may need both content assistance and system configuration help in same session
- **Email configuration**: Received专属邮箱iharvey@agentmail.to with access token; to be integrated into self-improvement system for feedback/reporting
- **Email integration**: Successfully implemented Python-based email integration with self-improving-agent; uses SMTP/IMAP for bidirectional communication; configured with OpenClaw cron for periodic monitoring and reporting