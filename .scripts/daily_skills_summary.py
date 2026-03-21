#!/usr/bin/env python3
"""
每日技能更新总结脚本
每天6:00和18:00执行，向James汇报
"""

import subprocess
import json
from datetime import datetime, timedelta
from pathlib import Path

SKILLS_DIR = Path("/Users/fhjtech/.openclaw/workspace/skills")
SKILLS_DB = Path("/Users/fhjtech/.openclaw/workspace/.learnings/skills_usage.json")
SUMMARY_FILE = Path("/Users/fhjtech/.openclaw/workspace/.learnings/daily_skills_summary.md")

def get_recently_installed():
    """获取最近安装的技能"""
    try:
        with open(SKILLS_DB, 'r') as f:
            data = json.load(f)
    except:
        return []
    
    today = datetime.now().date()
    recent = []
    
    for name, info in data.get("skills", {}).items():
        if info.get("status") == "auto-installed":
            installed_date = info.get("installed_date", "")
            if str(today) in installed_date or str(today - timedelta(days=1)) in installed_date:
                recent.append((name, info.get("description", "")))
    
    return recent

def generate_summary():
    """生成总结"""
    recent = get_recently_installed()
    total = len(list(SKILLS_DIR.iterdir()))
    
    summary = f"""## 每日技能更新总结

**时间**: {datetime.now().strftime("%Y-%m-%d %H:%M")}
**当前技能总数**: {total}

"""
    
    if recent:
        summary += "### 🆕 今日新安装技能\n\n"
        for name, desc in recent:
            summary += f"- **{name}**: {desc}\n"
        summary += "\n### 💡 使用建议\n\n"
        for name, desc in recent[:5]:
            summary += f"- {name}: 适用于{desc}\n"
    else:
        summary += "### ℹ️ 今日无新技能安装\n\n"
        summary += "技能库已保持最新状态。\n"
    
    return summary

def save_summary():
    """保存总结"""
    summary = generate_summary()
    with open(SUMMARY_FILE, 'w') as f:
        f.write(summary)
    return summary

def send_notification(summary):
    """发送飞书通知（通过OpenClaw message）"""
    # 这里通过print输出，由OpenClaw捕获并发送
    print(f"📊 每日技能总结\n{summary}")

def main():
    summary = save_summary()
    send_notification(summary)
    print("=== Daily Summary Completed ===")

if __name__ == "__main__":
    main()
