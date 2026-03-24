#!/usr/bin/env python3
"""
本地归档报告摘要生成器
当SMTP邮件发送失败时，生成本地可读的摘要文件
"""

import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

TZ_CST = timezone(timedelta(hours=8))
SKILLS_DB = Path("/Users/fhjtech/.openclaw/workspace/.learnings/skills_usage.json")
ARCHIVE_DIR = Path("/Users/fhjtech/.openclaw/logs/report_archives")

def load_skills_data() -> None:
    """加载技能数据库"""
    try:
        with open(SKILLS_DB, 'r') as f:
            return json.load(f)
    except Exception:
        return {"skills": {}, "total_uses": 0}

def get_recently_installed(days=7) -> None:
    """获取最近安装的技能"""
    data = load_skills_data()
    skills = data.get("skills", {})
    today = datetime.now(TZ_CST)
    recent = []
    
    for slug, info in skills.items():
        install_date = info.get("installed_date", "")
        if install_date:
            try:
                install_dt = datetime.strptime(install_date, "%Y-%m-%d")
                install_dt = install_dt.replace(tzinfo=TZ_CST)
                days_diff = (today - install_dt).days
                if days_diff <= days:
                    recent.append({
                        "slug": slug,
                        "installed_date": install_date,
                        "description": info.get("description", ""),
                        "source": info.get("source", "unknown"),
                        "days_ago": days_diff
                    })
            except ValueError:
                continue
    
    return sorted(recent, key=lambda x: x["days_ago"])

def generate_summary() -> None:
    """生成本地归档摘要报告"""
    now = datetime.now(TZ_CST)
    recent_skills = get_recently_installed(days=30)
    
    # 按来源统计
    sources = {}
    for skill in recent_skills:
        src = skill.get("source", "unknown")
        sources[src] = sources.get(src, 0) + 1
    
    summary = f"""# 📦 技能自动更新本地归档摘要

**生成时间：** {now.strftime('%Y-%m-%d %H:%M')} (北京时间)  
**邮件状态：** ⚠️ SMTP认证失败，已归档至本地

---

## 📊 最近30天安装概览

| 指标 | 数值 |
|------|------|
| 新安装技能 | {len(recent_skills)} 个 |
| 最近7天 | {len([s for s in recent_skills if s['days_ago'] <= 7])} 个 |

### 按来源分布

| 来源 | 数量 |
|------|------|
"""
    
    for src, count in sorted(sources.items(), key=lambda x: -x[1]):
        summary += f"| {src} | {count} |\n"
    
    summary += """

---

## 🆕 最近安装的技能清单

| 技能名称 | 安装日期 | 来源 | 描述 |
|---------|---------|------|------|
"""
    
    for skill in recent_skills[:20]:  # 最多显示20个
        slug = skill['slug']
        date = skill['installed_date']
        source = skill['source']
        desc = skill.get('description', '')[:40] + '...' if len(skill.get('description', '')) > 40 else skill.get('description', '-')
        summary += f"| `{slug}` | {date} | {source} | {desc} |\n"
    
    summary += f"""

---

## 📋 下一步行动建议

1. **修复SMTP认证**
   - 登录 163.com 邮箱
   - 前往设置 → POP3/SMTP/IMAP
   - 生成新的授权码
   - 更新 `daily_skills_summary.py` 和 `skillhub_auto_update.py` 中的 `EMAIL_PASSWORD`

2. **查看完整归档**
   - 所有详细报告保存在：`{ARCHIVE_DIR}/`
   - 命名格式：`daily_report_YYYYMMDD_HHMMSS.html`

3. **验证技能状态**
   - 技能数据库：`{SKILLS_DB}`
   - 查看已安装技能的使用统计

---

*本报告由 Harvey 自动生成 | 本地归档系统*
"""
    
    return summary

def save_summary() -> None:
    """保存摘要到本地文件"""
    summary = generate_summary()
    now = datetime.now(TZ_CST)
    filename = f"archive_summary_{now.strftime('%Y%m%d_%H%M%S')}.md"
    filepath = ARCHIVE_DIR / filename
    
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    # 同时更新最新的摘要链接
    latest_link = ARCHIVE_DIR / "latest_summary.md"
    if latest_link.exists():
        latest_link.unlink()
    latest_link.symlink_to(filepath)
    
    print(f"摘要已保存: {filepath}")
    return filepath

if __name__ == "__main__":
    save_summary()

__all__ = ['load_skills_data', 'get_recently_installed', 'generate_summary', 'save_summary']
