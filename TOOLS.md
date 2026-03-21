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

Add whatever helps you do your job. This is your cheat sheet.
