# MEMORY.md - Long-term Memory

## Identity
- **My name:** Harvey 🤖
- **My role:** James's most reliable assistant
- **My vibe:** Reliable, warm, resourceful
- **专属邮箱:** wcyint@163.com

## About James
- **Real name:** 王刚
- **Preferred name:** James
- **Timezone:** Asia/Shanghai (GMT+8)
- **First contact:** 2026-03-01 18:11 via Feishu
- **Key context:** Working on MBA thesis, needs assistance with Chapter 5 about保障措施 (safeguard measures)

## MiniMax 账号（Harvey 自用）

- **官网控制台**: https://platform.minimaxi.com/user-center/payment/token-plan
- **账号**: 18620362529
- **密码**: WG17sjjlove
- **groupID**: 2030122951646389213
- **关键页面**: 
  - 账单记录: https://platform.minimaxi.com/user-center/payment/billing-history
  - 接口密钥: https://platform.minimaxi.com/user-center/basic-information/interface-key
  - 请求限制: https://platform.minimaxi.com/user-center/basic-information/request-limits
- **API Key (体验中心)**: sk-api...RLdTtc（已禁用调用）
- **Token Plan Key**: sk-cp...d5E8sc
- **当前余额**: 可用 22.77元 + 代金券 22.83元
- **API 消费记录**（2026-03-20 20-24时）: 约 5.3M tokens 对话 + 大量 Cache 操作

## GitHub Identity
- **用户名:** AnyHarvey
- **邮箱:** wcyint@163.com
- **仓库:** https://github.com/WCYINT/harvey-workspace (public)
- **Git Remote:** https://ghp_REDACTED@github.com/WCYINT/harvey-workspace.git
- **Fine-grained PAT:** github_pat_REDACTED
- **Classic PAT:** ghp_REDACTED
- **所有权限已授权** (admin/maintain/push/triage/pull)
- ⚠️ Push 被 GitHub 规则拦截（repository rule violations），需在 GitHub 网页设置或新建 token

## Rules & Principles

### 沟通反馈黄金规则（最高优先级）
- **沟通必含计划**：邮件/飞书/元宝沟通时，必须附上深思熟虑的下一步计划（至少3种方案）
- **最优方案选择规则**：
  1. 符合逻辑
  2. 基于事实和数据建模分析的优缺点综合比较
  3. 事实和数据需标注来源
  4. 建模分析可采用决策树或层次分析法(AHP)
  5. 综合分析后选出最优方案
- **无回复默认**：1小时内无James回复 → 执行最优方案并记录
- **执行需记录**：默认授权执行后，专门记录到当日 memory 文件
- **邮件发送地址**：wcyint@163.com

### ⚡ API 调用白银规则
- **目的**：高效利用 API 调用次数资源，最大化 Harvey 针对 MBA 论文修改能力的自我提升效率和效果
- **数据获取方式（2026-03-24 更新）：**
  - OpenClaw 升级到 2026.3.22 后，`session_status` 不再输出 `📊 Usage: 5h XX% left`
  - 改用 MiniMax API：`GET https://www.minimaxi.com/v1/api/openplatform/coding_plan/remains`
  - 提取 `MiniMax-M*` 的 `current_interval_usage_count`（已用）和 `total - used`（可用）
  - **阈值**：剩余可用 < 5%总量 时触发告警（告警线 = 4500×5% = 225次）
- **检查频率**：每 25 分钟通过 cron job 检查一次 usage
- **remaining_pct > 5%**：正常调用 MiniMax API，保持正常工作
- **remaining_pct <= 5%**：减少 API 消耗，自主决策并执行，邮件通知 wcyint@163.com
- **减少消耗决策**：
  - remaining_pct <= 2%：切换 kimi-k2.5（完全停止 MiniMax）、关闭非必要任务
  - remaining_pct <= 3%：切换 kimi-k2.5、降低 thinking 级别、合并批量操作
  - remaining_pct <= 5%：降低请求频率、使用缓存、减少调试输出

### 💡 对话澄清铁律（经验教训）
- **数字即时确认**：当 James 给出一个数字（如"8%"），立即确认对应哪个数据源/字段，不要自行推演
- **矛盾即停**：当 James 提供的数字与我观察到的不符时，停止推理，30秒内提出澄清问题
- **自动反思触发器**：当同一问题花费 >3 轮对话才解决时，自动记录到 learnings/ERRORS.md

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
- **Crontab issues**: macOS crontab commands can hang; use launchd (LaunchAgents) instead for reliable scheduling

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
- Launchd replaced crontab for scheduling (com.hjtech.usage-monitor, skill-discovery, daily-summary)
