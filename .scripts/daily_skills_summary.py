#!/usr/bin/env python3
"""
每日技能更新总结脚本
每天6:00和18:00执行，通过Feishu API直接发送给James
"""

import subprocess
import json
import os
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

SKILLS_DIR   = Path("/Users/fhjtech/.openclaw/workspace/skills")
SKILLS_DB    = Path("/Users/fhjtech/.openclaw/workspace/.learnings/skills_usage.json")
SUMMARY_FILE = Path("/Users/fhjtech/.openclaw/workspace/.learnings/daily_skills_summary.md")
LOG_MARKER   = Path("/Users/fhjtech/.openclaw/workspace/.learnings/.last_update_summary.json")
TZ_CST       = timezone(timedelta(hours=8))

# ── Feishu 推送配置 ──────────────────────────────
APP_ID     = "cli_a90c7258f9b85bef"
APP_SECRET = "Kv6kG5ggU2TP9Ocw5CHSucu1B1t26J7t"
USER_OPEN_ID = "ou_7bc224841d2a1064cf5a7fbf67824227"

# ── Feishu API ──────────────────────────────────
def get_tenant_access_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode()
    req = urllib.request.Request(url, data=payload,
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.load(resp)
    if data.get("code") != 0:
        raise Exception(f"Token failed: {data}")
    return data["tenant_access_token"]

def send_text_message(token, receive_id, receive_id_type, content):
    url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type={receive_id_type}"
    payload = {
        "receive_id": receive_id,
        "msg_type": "text",
        "content": json.dumps({"text": content})
    }
    data = json.dumps(payload).encode()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.load(resp)

# ── 技能统计 ────────────────────────────────────
def get_recently_installed():
    """优先从上次自动更新的摘要文件读取，其次从数据库读取"""
    # 优先读自动更新写入的摘要
    try:
        with open(LOG_MARKER, 'r') as f:
            summary = json.load(f)
        today_str = datetime.now(TZ_CST).strftime("%Y-%m-%d")
        if summary.get("date") == today_str:
            return [(s["slug"], s["description"]) for s in summary.get("skills", [])]
    except:
        pass

    # 回退：从数据库读取
    try:
        with open(SKILLS_DB, 'r') as f:
            data = json.load(f)
    except:
        return []

    today = datetime.now(TZ_CST).date()
    recent = []
    for name, info in data.get("skills", {}).items():
        if info.get("status") == "auto-installed":
            installed_date = info.get("installed_date", "")
            if str(today) in installed_date or str(today - timedelta(days=1)) in installed_date:
                recent.append((name, info.get("description", "")))
    return recent

def count_skills():
    try:
        return len(list(SKILLS_DIR.iterdir()))
    except:
        return 0

def generate_summary():
    recent = get_recently_installed()
    total  = count_skills()
    now    = datetime.now(timezone(timedelta(hours=8)))

    lines = [
        f"📊 **每日技能更新总结**",
        f"🕗 时间：{now.strftime('%Y-%m-%d %H:%M')}",
        f"📦 当前技能总数：{total}",
        ""
    ]

    if recent:
        lines.append("🆕 **今日新安装技能**：")
        for name, desc in recent:
            lines.append(f"  • {name}：{desc}")
        lines.append("")
        lines.append("💡 **使用建议**：")
        for name, desc in recent[:5]:
            lines.append(f"  • {name} → {desc}")
    else:
        lines.append("ℹ️ 今日无新技能安装，技能库已保持最新状态。")

    return "\n".join(lines)

def save_summary_md(text):
    with open(SUMMARY_FILE, 'w') as f:
        f.write(text)

def main():
    summary = generate_summary()
    save_summary_md(summary)

    try:
        token = get_tenant_access_token()
        result = send_text_message(token, USER_OPEN_ID, "open_id", summary)
        if result.get("code") == 0:
            print(f"[{datetime.now()}] [OK] Feishu message sent successfully")
            print(summary)
        else:
            print(f"[{datetime.now()}] [ERROR] Feishu API error: {result}")
            print("[FALLBACK] Summary content:")
            print(summary)
    except Exception as e:
        print(f"[{datetime.now()}] [ERROR] Failed to send Feishu message: {e}")
        print("[FALLBACK] Summary content:")
        print(summary)

    print("=== Daily Summary Completed ===")

if __name__ == "__main__":
    main()
