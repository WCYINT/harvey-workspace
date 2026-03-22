#!/usr/bin/env python3
"""
每日技能更新 + 学习汇报脚本
每天 06:00 和 18:00 执行

内容：
1. 技能更新汇总（新安装/安全评估/集成结果）
2. Peter Steinberger 学习 (https://steipete.me + GitHub)
3. OpenClaw 官方动态 (https://openclaw.ai + GitHub/openclaw)

发送到: wgcapsa@163.com (James邮箱)
"""

import json
import smtplib
import subprocess
import urllib.request
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ── 配置 ──────────────────────────────────────────
SKILLS_DIR   = Path("/Users/fhjtech/.openclaw/workspace/skills")
SKILLS_DB    = Path("/Users/fhjtech/.openclaw/workspace/.learnings/skills_usage.json")
LOG_MARKER   = Path("/Users/fhjtech/.openclaw/workspace/.learnings/.last_update_summary.json")
SUMMARY_FILE = Path("/Users/fhjtech/.openclaw/workspace/.learnings/daily_learning_report.md")

# 邮件
EMAIL_FROM     = "wcyint@163.com"
EMAIL_TO       = "wcyint@163.com"
EMAIL_PASSWORD = "NDdE6mZyTMifExXL"
SMTP_HOST     = "smtp.163.com"
SMTP_PORT     = 465

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
        print(f"[{datetime.now(TZ_CST)}] [EMAIL] 发送成功 -> {EMAIL_TO}")
        return True
    except Exception as e:
        print(f"[{datetime.now(TZ_CST)}] [EMAIL] 失败: {e}")
        return False

# ── Peter Steinberger 学习 ─────────────────────
def learn_peter_steinberger() -> dict:
    """抓取 steipete.me 最新内容 + GitHub 活动"""
    result = {"articles": [], "github": [], "summary": ""}
    try:
        # 抓取博客
        req = urllib.request.Request(
            "https://steipete.me/",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode("utf-8", errors="ignore")
        # 提取文章标题和链接
        titles = re.findall(r'<h2[^>]*><a[^>]*href="([^"]+)"[^>]*>([^<]+)</a></h2>', content)
        dates = re.findall(r'<time[^>]*>([^<]+)</time>', content)
        for i, (url, title) in enumerate(titles[:5]):
            result["articles"].append({
                "title": title.strip(),
                "url": url,
                "date": dates[i] if i < len(dates) else ""
            })
    except Exception as e:
        result["summary"] = f"博客抓取失败: {e}"

    try:
        # GitHub activity
        req = urllib.request.Request(
            "https://api.github.com/users/steipete/events/public",
            headers={"User-Agent": "Mozilla/5.0", "Accept": "application/vnd.github.v3+json"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        for event in data[:10]:
            event_type = event.get("type", "")
            repo = event.get("repo", {}).get("name", "")
            created = event.get("created_at", "")[:10]
            result["github"].append(f"{created} {event_type}: {repo}")
    except Exception as e:
        result["github"].append(f"GitHub 抓取失败: {e}")

    return result

# ── OpenClaw 官方动态 ───────────────────────────
def learn_openclaw() -> dict:
    """抓取 OpenClaw 官网 + GitHub 最新动态"""
    result = {"news": [], "github_releases": [], "summary": ""}
    try:
        req = urllib.request.Request(
            "https://openclaw.ai/",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode("utf-8", errors="ignore")
        # 提取博客/新闻标题
        titles = re.findall(r'<h[23][^>]*><a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>', content)
        for url, title in titles[:5]:
            result["news"].append({"title": title.strip(), "url": url})
    except Exception as e:
        result["news"].append(f"官网抓取失败: {e}")

    try:
        req = urllib.request.Request(
            "https://api.github.com/repos/openclaw/openclaw/releases/latest",
            headers={"User-Agent": "Mozilla/5.0", "Accept": "application/vnd.github.v3+json"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        result["github_releases"].append({
            "tag": data.get("tag_name", ""),
            "name": data.get("name", ""),
            "body": data.get("body", "")[:300],
            "url": data.get("html_url", "")
        })
    except Exception as e:
        result["github_releases"].append(f"GitHub Releases 抓取失败: {e}")

    return result

# ── 读取新安装技能 ─────────────────────────────
def get_new_skills():
    try:
        with open(LOG_MARKER, 'r') as f:
            summary = json.load(f)
        today_str = datetime.now(TZ_CST).strftime("%Y-%m-%d")
        if summary.get("date") == today_str:
            return summary.get("skills", [])
    except:
        pass
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
                    "source": info.get("source", "")
                })
    return new

# ── 生成报告 ───────────────────────────────────
def generate_report(new_skills, total, peter_data, openclaw_data):
    now = datetime.now(TZ_CST)
    now_str = now.strftime('%Y-%m-%d %H:%M')

    # 技能部分
    if new_skills:
        skills_rows = ""
        for s in new_skills:
            skills_rows += f"<tr><td><code>{s['slug']}</code></td><td>{s.get('source','')}</td><td>{s['description'][:80]}</td></tr>"
        skills_html = f"""
        <h2>📦 技能更新</h2>
        <p>今日新安装：<b>{len(new_skills)}</b> 个 | 技能库总数：<b>{total}</b></p>
        <table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;width:100%">
            <tr style="background:#f0f0f0"><th>技能</th><th>来源</th><th>描述</th></tr>
            {skills_rows}
        </table>"""
    else:
        skills_html = f"<h2>📦 技能更新</h2><p>今日无新安装（技能库已最新）。技能库总数：<b>{total}</b></p>"

    # Peter Steinberger 部分
    peter_articles = ""
    for a in peter_data.get("articles", [])[:5]:
        if isinstance(a, dict):
            peter_articles += f"<li><a href='{a['url']}'>{a['title']}</a> ({a.get('date','')})</li>"
        else:
            peter_articles += f"<li>{a}</li>"
    peter_gh = ""
    for g in peter_data.get("github", [])[:10]:
        peter_gh += f"<li style='font-family:monospace;font-size:13px'>{g}</li>"
    peter_html = f"""
    <h2>🧑‍💻 Peter Steinberger 学习</h2>
    <p><a href='https://steipete.me'>https://steipete.me</a> | 
       <a href='https://github.com/steipete'>GitHub</a></p>
    <h3>最新文章</h3>
    <ul>{peter_articles or '<li>暂无</li>'}</ul>
    <h3>GitHub 活动</h3>
    <ul>{peter_gh or '<li>暂无</li>'}</ul>
    <h3>💡 关键心得</h3>
    <p>Peter 是 iOS 开发出身（PSPDFKit 作者），后转型 AI 工具专家并加入 OpenAI 做 Agent 开发。
       他的职业路径：从 Swift 专家 → AI Agent 开发者 → 行业影响者。
       启示：深度垂直领域专家经验 + AI 工具化能力 = 强大竞争力。</p>"""

    # OpenClaw 部分
    oc_news = ""
    for n in openclaw_data.get("news", [])[:5]:
        if isinstance(n, dict):
            oc_news += f"<li><a href='{n['url']}'>{n['title']}</a></li>"
        else:
            oc_news += f"<li>{n}</li>"
    oc_releases = ""
    for r in openclaw_data.get("github_releases", []):
        if isinstance(r, dict):
            oc_releases += f"<li><b>{r.get('tag','')}</b>: {r.get('name','')} — <a href='{r.get('url','')}'>查看</a><br><pre style='font-size:12px'>{r.get('body','')[:200]}</pre></li>"
        else:
            oc_releases += f"<li>{r}</li>"
    openclaw_html = f"""
    <h2>🤖 OpenClaw 官方动态</h2>
    <p><a href='https://openclaw.ai'>官网</a> | 
       <a href='https://github.com/openclaw/openclaw'>GitHub</a> | 
       <a href='https://discord.com/invite/clawd'>Discord</a></p>
    <h3>最新动态</h3>
    <ul>{oc_news or '<li>暂无</li>'}</ul>
    <h3>最新 Release</h3>
    <ul>{oc_releases or '<li>暂无</li>'}</ul>"""

    body = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"></head>
<body style="font-family:Arial,sans-serif;max-width:900px;margin:0 auto;padding:20px">
    <h1>📊 Harvey 每日汇报</h1>
    <p><b>时间：</b>{now_str} (北京时间)</p>
    <hr>
    {skills_html}
    <hr>
    {peter_html}
    <hr>
    {openclaw_html}
    <hr>
    <p style="color:#888;font-size:12px">
        由 Harvey 自动生成 | 四源技能发现系统 | 
        四步学习：Peter Steinberger + OpenClaw 官方<br>
        永久规则 · 不可删除
    </p>
</body></html>"""
    return body

# ── 主流程 ──────────────────────────────────────
def main():
    new_skills = get_new_skills()
    try:
        total = len([d for d in SKILLS_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")])
    except:
        total = 0

    print(f"[{datetime.now(TZ_CST)}] 学习 Peter Steinberger...")
    peter_data = learn_peter_steinberger()
    print(f"[{datetime.now(TZ_CST)}] 学习 OpenClaw...")
    openclaw_data = learn_openclaw()

    html_body = generate_report(new_skills, total, peter_data, openclaw_data)
    now_str = datetime.now(TZ_CST).strftime('%m-%d %H:%M')
    subject = f"📊 Harvey 每日汇报 | {now_str} | {len(new_skills)} 个新技能"

    # 保存本地
    with open(SUMMARY_FILE, 'w', encoding='utf-8') as f:
        f.write(html_body)

    # 发送邮件
    email_ok = send_email(subject, html_body)
    print(f"[{datetime.now(TZ_CST)}] === 每日汇报完成: {'OK' if email_ok else 'FAIL'} ===")

if __name__ == "__main__":
    main()
