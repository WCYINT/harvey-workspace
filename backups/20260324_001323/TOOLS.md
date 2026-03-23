# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

### 📬 沟通反馈黄金规则

**通过邮件、飞书、元宝派反馈沟通时：**
- 必须附上深思熟虑后的**下一步计划**
- 至少提供**3种针对性方案**供决策
- **最优方案选择规则**（必须符合以下逻辑）：
  1. 符合逻辑
  2. 经过**基于事实**的优缺点比较
  3. 经过**数据建模分析**的优缺点综合比较
  4. 事实和数据需**标注来源**
  5. 建模分析可采用**决策树**或**层次分析法(AHP)**
  6. 综合分析后选出最优方案
- James 1小时内无回复 → 默认执行最优方案并记录

**执行默认规则：** 邮件发出后1小时无回复 = 获得授权按建议执行

**邮件发送地址：** wcyint@163.com

### ⚡ API 使用白银规则

**目的：** 高效利用 API 调用次数资源，最大化 Harvey 针对 MBA 论文修改能力的自我提升效率和效果

**session_status 正确解读（铁律）：**
```
📊 Usage: 5h 13% left ⏱2h 18m
      ↓      ↓          ↓
   时间段   已用%      剩余时间
```
- `5h` = 时间段总长（5小时窗口）
- `13%` = 已消耗的 API 调用次数占比
- `⏱2h 18m` = 该时间段剩余时间

**阈值定义：** 95% 阈值指的是 `5h XX% left` 中的 `XX%`，即5小时窗口内已消耗的 API 调用次数比例。

**执行步骤：**
1. 每 25 分钟通过 OpenClaw cron job 检查一次 MiniMax API usage
2. 调用 session_status 工具获取 `5h XX% left` 格式数据
3. **usage < 95%** → 正常调用 MiniMax API，保持正常工作
4. **usage >= 95%** → 减少 API 消耗，自主做出减少消耗决策并执行，邮件通知 wcyint@163.com

**减少消耗决策规则：**
- usage >= 99%：切换 kimi-k2.5（完全停止 MiniMax）、关闭非必要任务
- usage >= 97%：切换 kimi-k2.5、降低 thinking 级别、合并批量操作
- usage >= 95%：降低请求频率、使用缓存、减少调试输出

### 💡 对话澄清铁律（经验教训）

**问题根源：** 花费太多时间在错误理解上，而不是快速确认。

**铁律1 - 数字即时确认：**
当 James 给出一个数字（如"8%"），立即确认：
> "你说的 X% 是 session_status 输出中 `5h XX% left` 的 XX% 吗？"
不要自行推演，不要假设。

**铁律2 - 矛盾即停：**
当 James 提供的数字与我观察到的不符时，停止推理，立即澄清：
- 禁止：在澄清前花费 >2 分钟继续推理
- 必须：30秒内提出澄清问题

**铁律3 - 自动反思触发器：**
当同一问题花费 >3 轮对话才解决时，自动记录到 learnings/ERRORS.md：
- 记录问题类型、解决过程、教训
- 防止同类问题重复发生

---

### Harvey 专属邮箱

- **邮箱:** wcyint@163.com
- **授权码:** NDdE6mZyTMifExXL
- **POP3:** pop.163.com (SSL, 端口 995)
- **SMTP:** smtp.163.com (SSL, 端口 465)
- **IMAP:** imap.163.com (SSL, 端口 993)

### 深圳图书馆数字资源账号

- **数字资源入口**: https://er.szlib.org.cn:8899/https/vpn/4/P75YPLUDN3WXTLUPMW4A/
- **资源首页**: https://www.szlib.org.cn/digitalResource/index.html
- **账号**: 0440070088520
- **密码**: WG17sjjlove
- **用途**: 查找国内期刊（维普等）和国外学术资料

---

### MiniMax 账号（Harvey 自用）

- **官网控制台**: https://platform.minimaxi.com/user-center/payment/token-plan
- **账号**: 18620362529
- **密码**: WG17sjjlove
- **用途**: MiniMax M2.7/M2.5 API 调用，Harvey 主要用 minimax-cn

---

### Python 进化成果（2026-03-21）

**已掌握的生产级组件：**

| 组件 | 路径 | 说明 |
|------|------|------|
| AsyncScheduler | `.scripts/async_scheduler.py` | asyncio并发调度，18.5x加速 |
| MiniMax Client | `.scripts/minimax_client.py` | M2.7对话/TTS/Embedding |
| Design Patterns | `.scripts/design_patterns.py` | 工厂/策略/观察者模式 |
| AsyncHTTP | `.scripts/async_http.py` | httpx并发客户端+重试 |
| Config Manager | `.scripts/config_manager.py` | pydantic配置验证 |
| Health Check | `.scripts/self_health_check.py` | 守护进程+自动重启 |
| SkillHub Auto | `.scripts/skillhub_auto_update.py` | 六步技能更新 |
| Daily Report | `.scripts/daily_skills_summary.py` | 邮件+飞书日报 |

**关键命令：**
```bash
# 类型检查
mypy .scripts/ --strict --ignore-missing-imports

# 运行测试
pytest .scripts/tests/ -v --tb=short

# Benchmark
python3 .scripts/async_scheduler.py

# CI/CD（Docker）
docker build -f .docker/Dockerfile . -t harvey-workspace
```

**Python 能力：~68% → ~90%（今日提升22个百分点）**

---

---

### 🏭 gstack AskUserQuestion 决策框架

**来源**：gstack（garrytan/gstack，Y Combinator总裁开源的多角色开发框架）

**核心**：遇到复杂决策时的结构化思考框架，替代"凭直觉选择"。

**格式（严格4步）：**

```
1. Re-ground（重新聚焦）
   → 陈述项目背景、当前任务、已知事实
   → 1-2句话，不要超过3行

2. Simplify（简化说明）
   → 用简单语言解释需要什么（8年级学生能看懂）
   → 不用技术术语，不用内部行话
   → 说"是什么"而不是"叫什么"

3. Recommend（推荐方案）
   → RECOMMENDATION: 选择 X
   → 推荐理由（1句话）
   → Completeness: X/10（10=完整实现，7=覆盖主要路径，5=捷径）
   → 如果两个选项都≥8分，选更高的；如果任一≤5分，标记它

4. Options（选项）
   → A) ... （描述，含工作量估算）
   → B) ... （描述，含工作量估算）
   → C) ... （描述，含工作量估算）
   → 每个选项都要说 human时间和AI时间
```

**使用时机：**
- 技能选择/方案对比
- 问题判断（选A还是B）
- 复杂多维度决策
- 任何需要向 King 汇报并等待决策的时刻

**输出格式（在汇报末尾）：**

```
📋 下一步计划（需King决策）

| 方案 | 描述 | 优点 | 缺点 |
| --- | --- | --- | --- |
| A | ... | ... | ... |
| B | ... | ... | ... |

RECOMMENDATION: 方案X
理由：...

⏱️ 若1小时内无回复，默认执行推荐方案
```

**Completeness 评分参考（gstack Boil the Lake原则）：**

| 任务类型 | 完整实现 | 捷径版本 | 说明 |
|---------|---------|---------|------|
| 论文数据分析 | 完整DOE+回归+可视化 | 只做描述统计 | 10 vs 7 |
| 技能安装 | 4平台全量搜索+测试 | 只装最热门3个 | 10 vs 6 |
| 论文修改 | 全稿逻辑检查+润色 | 只改重点章节 | 10 vs 7 |

**注意：** AI让完整实现的边际成本≈0，因此Completeness 8/10以上的选项通常更值得选择。

---

Add whatever helps you do your job. This is your cheat sheet.
