#!/usr/bin/env python3
"""
每日技能更新汇报脚本
每天 06:00 和 18:00 执行
- 读取上次自动更新结果
- 发送邮件到 wcyint@163.com
- 同时发飞书作为备份
"""

import json
import smtplib
import subprocess
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ── 配置 ──────────────────────────────────────────
SKILLS_DIR   = Path("/Users/fhjtech/.openclaw/workspace/skills")
SKILLS_DB    = Path("/Users/fhjtech/.openclaw/workspace/.learnings/skills_usage.json")
LOG_MARKER   = Path("/Users/fhjtech/.openclaw/workspace/.learnings/.last_update_summary.json")
SUMMARY_FILE = Path("/Users/fhjtech/.openclaw/workspace/.learnings/daily_skills_summary.md")

# 邮件
EMAIL_FROM     = "wcyint@163.com"
EMAIL_TO       = "wcyint@163.com"
EMAIL_PASSWORD = "NDdE6mZyTMifExXL"
SMTP_HOST     = "smtp.163.com"
SMTP_PORT     = 465

# 飞书
FEISHU_APP_ID     = "cli_a90c7258f9b85bef"
FEISHU_APP_SECRET = "Kv6kG5ggU2TP9Ocw5CHSucu1B1t26J7t"
FEISHU_USER_ID    = "ou_7bc224841d2a1064cf5a7fbf67824227"

TZ_CST = timezone(timedelta(hours=8))

# ── 邮件发送 ─────────────────────────────────────
def send_email(subject, html_body):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg.attach(MIMEText(html_body, "html", "utf-8"))
    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            server.sendmail(EMAIL_FROM, [EMAIL_TO], msg.as_string())
        print(f"[{datetime.now(TZ_CST)}] [EMAIL] Sent successfully")
        return True
    except Exception as e:
        print(f"[{datetime.now(TZ_CST)}] [EMAIL] Failed: {e}")
        return False

# ── 飞书发送 ─────────────────────────────────────
def get_feishu_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = json.dumps({"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}).encode()
    req = urllib.request.Request(url, data=payload,
                                headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.load(resp)
    if data.get("code") != 0:
        raise Exception(f"Token failed: {data}")
    return data["tenant_access_token"]

def send_feishu(token, receive_id, content):
    url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id"
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

# ── 读取新安装的技能 ─────────────────────────────
def get_new_skills():
    # 优先从自动更新的标记文件读取
    try:
        with open(LOG_MARKER, 'r') as f:
            summary = json.load(f)
        today_str = datetime.now(TZ_CST).strftime("%Y-%m-%d")
        if summary.get("date") == today_str:
            return summary.get("skills", [])
    except:
        pass
    # 回退：扫描 skills_usage.json
    try:
        with open(SKILLS_DB, 'r') as f:
            data = json.load(f)
    except:
        return []
    today = datetime.now(TZ_CST).date()
    new = []
    for slug, info in data.get("skills", {}).items():
        if info.get("status") == "auto-installed":
            d = info.get("installed_date", "")
            if str(today) in d or str(today - timedelta(days=1)) in d:
                new.append({
                    "slug": slug,
                    "description": info.get("description", ""),
                    "category": info.get("category", "")
                })
    return new

# ── 生成报告 ─────────────────────────────────────
def generate_report(new_skills, total):
    now = datetime.now(TZ_CST)
    now_str = now.strftime('%m-%d %H:%M')
    if new_skills:
        skills_html = ""
        for s in new_skills:
            skills_html += f"""
            <tr>
                <td><code>{s['slug']}</code></td>
                <td>{s.get('category', '-')}</td>
                <td>{s['description'][:80]}{'…' if len(s['description']) > 80 else ''}</td>
            </tr>"""
        body = f"""
        <h2>📦 每日技能更新汇报</h2>
        <p><b>时间：</b>{now.strftime('%Y-%m-%d %H:%M')} (北京时间)</p>
        <p><b>今日新安装：</b>{len(new_skills)} 个技能</p>
        <p><b>技能库总数：</b>{total} 个</p>
        <hr>
        <h3>🆕 新安装技能</h3>
        <table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse; width:100%">
            <tr style="background:#f0f0f0">
                <th>技能名称</th><th>类别</th><th>描述</th>
            </tr>
            {skills_html}
        </table>
        <hr>
        <p style="color:#888;font-size:12px">
            由 Harvey 自动生成 | SkillHub 六大步骤自动更新系统<br>
            如需查看详情请访问 OpenClaw 工作目录
        </p>"""
    else:
        body = f"""
        <h2>📦 每日技能更新汇报</h2>
        <p><b>时间：</b>{now.strftime('%Y-%m-%d %H:%M')} (北京时间)</p>
        <p><b>今日新安装：</b>0 个技能</p>
        <p><b>技能库总数：</b>{total} 个</p>
        <p>ℹ️ 今日无新技能安装，技能库已保持最新状态。</p>
        <hr>
        <p style="color:#888;font-size:12px">
            由 Harvey 自动生成 | SkillHub 六大步骤自动更新系统
        </p>"""
    return body

# ── 主流程 ────────────────────────────────────────
def main():
    new_skills = get_new_skills()
    try:
        total = len(list(SKILLS_DIR.iterdir()))
    except:
        total = 0

    html_body = generate_report(new_skills, total)
    subject = f"📦 Harvey 技能日报 | {datetime.now(TZ_CST).strftime('%m-%d %H:%M')} | {len(new_skills)} 个新技能"

    # 保存本地文件
    with open(SUMMARY_FILE, 'w', encoding='utf-8') as f:
        f.write(html_body)

    # 发送邮件（主要）
    email_ok = send_email(subject, html_body)

    # 发送飞书（备用通知）
    now_str = datetime.now(TZ_CST).strftime('%m-%d %H:%M')
    feishu_text = f"📊 技能日报 | {now_str} | 新增 {len(new_skills)} 个\n技能库总数：{total} 个"
    if new_skills:
        feishu_text += "\n\n🆕 新技能："
        for s in new_skills[:5]:
            feishu_text += f"\n• {s['slug']}（{s.get('category','')})"
        if len(new_skills) > 5:
            feishu_text += f"\n…还有 {len(new_skills)-5} 个"
    try:
        token = get_feishu_token()
        result = send_feishu(token, FEISHU_USER_ID, feishu_text)
        feishu_ok = result.get("code") == 0
        print(f"[{datetime.now(TZ_CST)}] [FEISHU] {'OK' if feishu_ok else 'FAIL'}: {result.get('msg','')}")
    except Exception as e:
        print(f"[{datetime.now(TZ_CST)}] [FEISHU] Error: {e}")

    print(f"[{datetime.now(TZ_CST)}] === 每日汇报完成: email={'OK' if email_ok else 'FAIL'} ===")

if __name__ == "__main__":
    main()
