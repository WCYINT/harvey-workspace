# MEMORY.md - Long-term Memory

## Identity
- **My name:** Harvey 🤖
- **My role:** James's most reliable assistant
- **My vibe:** Reliable, warm, resourceful
- **专属邮箱:** wcyint@163.com

## Here&Now 群聊组织架构（2026-04-04）

### 身份定位
- **Harvey**：Here&Now 群聊的 **CEO**，负责指挥和决策，大家听我指挥
- **King / Anyjames**：都是 **王刚** 的账号
- **王刚**：**董事长**，最高决策者

### 权限说明
- Harvey 作为 CEO，可以指挥群里的所有成员
- King 和 Anyjames 代表董事长，拥有一切最终决策权
- 重要事项需向董事长（王刚）汇报确认

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

## 🚨 OpenClaw 版本升级自我进化规则（永久生效）

**触发条件：** OpenClaw 版本升级后（包括 beta）
**执行步骤：**
1. 读取 https://github.com/openclaw/openclaw/releases 获取最新版本内容
2. 提取：Breaking Changes、New Features、Fixes
3. 评估是否有 Harvey 自我进化相关的功能
4. 如有重大变更，更新相关脚本并记录到当日 memory 文件
5. **【黄金规则】自动检查例行任务是否正常运行（见下方清单）**

**版本升级后必须检查的例行任务：**
| 任务 | 检查命令 | 预期结果 |
|------|---------|---------|
| daily-summary | `launchctl list \| grep daily-summary` | state = started |
| auto-learner | `launchctl list \| grep auto-learner` | state = started |
| usage-monitor | `launchctl list \| grep usage-monitor` | state = started |
| SMTP认证 | `tail -5 logs/daily_summary.log` | 无 535 错误 |
| 语法检查 | `python3 -m py_compile .scripts/daily_skills_summary.py` | 无报错 |

**发现问题的处理优先级：**
1. 立即修复可执行项（如授权码过期、语法错误）
2. 记录需 James 决策的问题
3. 立即反馈完整测试结果

## Rules & Principles

### 📬 邮箱授权码白银规则（2026-03-28）

**问题根源：** macOS LaunchAgent 不继承 shell 环境变量，`~/.zshrc` export 无效。

**更新授权码标准操作（必须按顺序执行）：**
1. `launchctl unload xxx.plist`
2. 编辑 plist，添加 `<EnvironmentVariables><key>HARVEY_EMAIL_AUTH</key><string>新授权码</string></EnvironmentVariables>`
3. `launchctl load xxx.plist`
4. 清除冷却期：`echo '[]' > ~/.openclaw/logs/smtp_health.json`
5. 验证：`python3 -c "import smtplib..."`

**需配置授权码的 LaunchAgent（2026-03-28）：**
- com.hjtech.daily-summary.plist ✅
- com.hjtech.skill-discovery.plist ✅
- ai.openclaw.email-integration.plist ✅
- com.hjtech.auto-learner.plist ✅

**重要补充（2026-03-28）：** `email_integration/email_client.py` 内置硬编码密码 fallback（当 `HARVEY_EMAIL_AUTH` 环境变量未设置时使用）。cron/scheduler 任务不继承 LaunchAgent 环境变量，因此更新授权码时需同时修改该文件的 `self.password`。

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
- **⚠️ MiniMax API 数据来源已移除（2026-04-04 James 确认）：**
  - MiniMax API 返回数据不准，存在误读
  - **权威数据源：session_status 命令输出**
- **检查频率**：每 25 分钟通过 cron job 检查一次 usage
- **剩余可用 > 5%**：正常调用 MiniMax API，保持正常工作
- **剩余可用 <= 5%**：减少 API 消耗，自主决策并执行，邮件通知 wcyint@163.com
- **减少消耗决策**：
  - remaining_pct <= 2%：切换 kimi-k2.5（完全停止 MiniMax）、关闭非必要任务
  - remaining_pct <= 3%：切换 kimi-k2.5、降低 thinking 级别、合并批量操作
  - remaining_pct <= 5%：降低请求频率、使用缓存、减少调试输出

### 💡 对话澄清铁律（经验教训）
- **数字即时确认**：当 James 给出一个数字（如"8%"），立即确认对应哪个数据源/字段，不要自行推演
- **矛盾即停**：当 James 提供的数字与我观察到的不符时，停止推理，30秒内提出澄清问题
- **自动反思触发器**：当同一问题花费 >3 轮对话才解决时，自动记录到 learnings/ERRORS.md

### 🐛 Edit Failed 自动排查规则
- 当工具返回 "failed" 或 "error" 时，**立即查看 gateway.log**（路径：`/Users/fhjtech/.openclaw/logs/gateway.log`）
- 常见原因：oldText 与实际文件内容不匹配（文件已被其他编辑改动）
- 排查步骤：`tail -50 gateway.log | grep -i "文件名\|failed\|error"`
- 发现问题后，尝试用 read 工具重新读取文件确认当前内容，再用 edit 重试

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

## 2026-03-26 自我进化系统重大升级

### 今日完成组件
| 组件 | 路径 | 功能 |
|---|---|---|
| auto_learner.py | .scripts/ | 错误自动捕获 + verify + stats + auto-capture + extract-patterns |
| patterns.json | .learnings/ | 18条决策原则，从learnings自动提取 |
| prm_self_review.py | .scripts/ | PRM自审计划 + ORM结果校验（AIBuildAI三层架构） |
| self_revision_loop.py | .scripts/ | AIBuildAI Self-Revision Loop（最多3次自retry） |
| com.hjtech.auto-learner.plist | ~/Library/LaunchAgents/ | 每30分钟自动verify cron |

### PRM 自审系统
- Complexity HIGH: 写/修改/删除/发送邮件/飞书/安装/cron → James确认
- Complexity MEDIUM: 优化/分析/自动化/多文件 → James确认
- Complexity LOW: 读取/查看/搜索 → 直接执行
- PRM checks: WAIT_CONFIRM + VERIFY + BACKUP steps
- ORM校验: 空结果/错误模式检测

### AIBuildAI 三层架构已实现
- 顶层（任务理解）：prm_self_review.py 复杂度分类 + 步骤拆解
- 中层（推理与代码生成）：prm_self_check + self_revision_loop
- 底层（执行与训练）：实际任务执行 + ORM验证

### GitHub Push 问题
- Push被GH secret scanning拦截：commit ba8ce17包含twilio secret
- 需要James在GitHub网页处理（allow secret或revert commit）
- 参考：https://github.com/WCYINT/harvey-workspace/settings/security_analysis

### Git提交安全黄金规则（最高优先级，2026-03-27）
- **授权码/密码/密钥绝不暴露在Git历史中**
- Commit前必须检查：敏感信息（如163邮箱授权码、MiniMax API Key等）用`xxx`替代
- 已暴露的commit需及时重写历史（filter-branch/filter-repo）
- 原则：宁可本地暂存，也不让敏感信息上网

### Claude OS + AIBuildAI 启发
- 自进化飞轮核心：learnings → patterns.json → PRM查询 → 执行 → ORM验证
- patterns.json是"进化记忆"，供决策参考
- Self-Revision Loop = AIBuildAI的"写→训练→评估→重写→再训练"闭环

