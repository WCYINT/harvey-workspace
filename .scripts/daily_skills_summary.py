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
ARCHIVE_DIR = Path("/Users/fhjtech/.openclaw/logs/report_archives")
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

# SMTP Health Check State
SMTP_HEALTH_LOG = Path("/Users/fhjtech/.openclaw/logs/smtp_health.json")

def check_smtp_health() -> dict:
    """Proactive SMTP health check - returns status without sending actual email"""
    result = {
        "timestamp": datetime.now(TZ_CST).isoformat(),
        "status": "unknown",
        "latency_ms": 0,
        "auth_test": False,
        "error": None,
        "recommendation": None
    }
    
    import socket
    start_time = datetime.now()
    
    try:
        # Test TCP connection first
        sock = socket.create_connection((SMTP_HOST, SMTP_PORT), timeout=10)
        sock.close()
        
        # Test SMTP connection and auth
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.ehlo()
            # Try login - this will fail with 535 if auth code expired
            try:
                server.login(EMAIL_FROM, EMAIL_PASSWORD)
                result["auth_test"] = True
                result["status"] = "healthy"
            except smtplib.SMTPAuthenticationError as e:
                result["status"] = "auth_failed"
                result["error"] = f"SMTP 535 Auth Failed: {e}"
                result["recommendation"] = "AUTH_CODE_EXPIRED"
                
    except socket.timeout:
        result["status"] = "timeout"
        result["error"] = f"Connection to {SMTP_HOST}:{SMTP_PORT} timed out"
        result["recommendation"] = "CHECK_NETWORK"
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        result["recommendation"] = "CHECK_CONFIG"
    
    result["latency_ms"] = int((datetime.now() - start_time).total_seconds() * 1000)
    
    # Save health state
    try:
        health_history = []
        if SMTP_HEALTH_LOG.exists():
            with open(SMTP_HEALTH_LOG) as f:
                health_history = json.load(f)
        health_history.append(result)
        # Keep last 100 entries
        health_history = health_history[-100:]
        with open(SMTP_HEALTH_LOG, "w") as f:
            json.dump(health_history, f, indent=2)
    except Exception as e:
        print(f"[HEALTH] Failed to save health log: {e}")
    
    return result

def get_smtp_health_summary() -> str:
    """Get a summary of SMTP health for inclusion in reports"""
    if not SMTP_HEALTH_LOG.exists():
        return "<p>⚠️ No SMTP health data available yet</p>"
    
    try:
        with open(SMTP_HEALTH_LOG) as f:
            history = json.load(f)
        
        if not history:
            return "<p>⚠️ No SMTP health history</p>"
        
        # Get last 24 hours of checks
        recent = [h for h in history if 
                 (datetime.now(TZ_CST) - datetime.fromisoformat(h["timestamp"])).total_seconds() < 86400]
        
        if not recent:
            return "<p>⚠️ No recent SMTP health checks (last 24h)</p>"
        
        # Calculate stats
        healthy = sum(1 for h in recent if h["status"] == "healthy")
        auth_failures = sum(1 for h in recent if h["status"] == "auth_failed")
        
        latest = recent[-1]
        status_color = "✅" if latest["status"] == "healthy" else "❌"
        status_text = "健康" if latest["status"] == "healthy" else latest["status"]
        
        html = f"""
        <h4>{status_color} SMTP 健康状态 (最近24小时)</h4>
        <ul>
            <li>检查次数: {len(recent)} 次</li>
            <li>健康/成功: {healthy} 次 ({100*healthy//len(recent)}%)</li>
            <li>认证失败: {auth_failures} 次</li>
            <li>最新状态: <b>{status_text}</b> (延迟: {latest.get('latency_ms', 'N/A')}ms)</li>
        </ul>
        """
        
        if latest["status"] == "auth_failed":
            html += """
            <p style="color:#c00"><b>⚠️ 认证失败 - 授权码可能已过期</b></p>
            <p>请按以下步骤修复：</p>
            <ol>
                <li>登录 163.com 邮箱</li>
                <li>进入设置 -> POP3/SMTP/IMAP</li>
                <li>关闭 SMTP，重新开启</li>
                <li>生成新的授权码</li>
                <li>更新 daily_skills_summary.py 中的 EMAIL_PASSWORD</li>
            </ol>
            """
        
        return html
        
    except Exception as e:
        return f"<p>⚠️ Error reading SMTP health: {e}</p>"

def archive_report(subject: str, html_body: str) -> str:
    """Save report locally when email fails"""
    timestamp = datetime.now(TZ_CST).strftime("%Y%m%d_%H%M%S")
    filename = f"daily_report_{timestamp}.html"
    filepath = ARCHIVE_DIR / filename
    
    full_html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>{subject}</title></head>
<body style="font-family:Arial,sans-serif;max-width:900px;margin:0 auto;padding:20px">
<h1>📊 Harvey 每日汇报 (Archived)</h1>
<p><b>原定发送时间：</b>{datetime.now(TZ_CST).strftime('%Y-%m-%d %H:%M')} (Asia/Shanghai)</p>
<p><b>邮件发送状态：</b>❌ 失败 (已归档到本地)</p>
<hr>
{html_body}
<hr>
<p style="color:#888;font-size:12px">归档路径: {filepath}</p>
</body></html>"""
    
    filepath.write_text(full_html, encoding="utf-8")
    return str(filepath)

def send_email_with_retry(subject, html_body, max_retries=3) -> None:
    """Send email with exponential backoff retry"""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg.attach(MIMEText(html_body, "html", "utf-8"))
    
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=30) as server:
                server.login(EMAIL_FROM, EMAIL_PASSWORD)
                server.sendmail(EMAIL_FROM, [EMAIL_TO], msg.as_string())
            print(f"[{datetime.now(TZ_CST)}] [EMAIL] 发送成功 -> {EMAIL_TO} (attempt {attempt})")
            return True
        except smtplib.SMTPAuthenticationError as e:
            last_error = f"SMTP Auth failed (535): {e}"
            # Don't retry auth errors - they won't succeed
            break
        except Exception as e:
            last_error = str(e)
            if attempt < max_retries:
                wait_time = 2 ** attempt  # Exponential backoff: 2s, 4s, 8s
                print(f"[{datetime.now(TZ_CST)}] [EMAIL] Attempt {attempt} failed, retrying in {wait_time}s...")
                import time
                time.sleep(wait_time)
    
    # All retries exhausted or auth error - archive locally
    archive_path = archive_report(subject, html_body)
    error_msg = f"[{datetime.now(TZ_CST)}] [EMAIL] 失败 (archived to {archive_path}): {last_error}"
    print(error_msg)
    
    # Log detailed diagnostics for SMTP auth issues
    if "535" in str(last_error) or "authentication" in str(last_error).lower():
        diag_msg = f"""
[{datetime.now(TZ_CST)}] [EMAIL-DIAGNOSTICS] SMTP Authentication Failed (535)
  - Error: {last_error}
  - Server: {SMTP_HOST}:{SMTP_PORT} (SSL)
  - From: {EMAIL_FROM}
  - To: {EMAIL_TO}
  - Possible causes:
    1. Authorization code expired (163.com codes expire after ~6-12 months)
    2. Account security settings changed
    3. Too many failed login attempts triggered temporary lockout
  - Resolution steps:
    1. Log into 163.com webmail
    2. Go to Settings -> POP3/SMTP/IMAP
    3. Disable then re-enable SMTP
    4. Generate NEW authorization code (授权码)
    5. Update EMAIL_PASSWORD in daily_skills_summary.py
  - Archived report saved to: {archive_path}
"""
        print(diag_msg)
        # Also write to a dedicated error log
        error_log = Path("/Users/fhjtech/.openclaw/logs/smtp_errors.log")
        with open(error_log, "a") as f:
            f.write(diag_msg)
    
    return False

def send_email(subject, html_body) -> None:
    """Backward-compatible wrapper"""
    return send_email_with_retry(subject, html_body)

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
def get_new_skills() -> None:
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
def generate_report(new_skills, total, peter_data, openclaw_data) -> None:
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

    next_steps = """
    <h2>📋 下一步计划</h2>
    <ul>
        <li><b>短期（本周）：</b>根据今日汇报中的新技能列表，筛选与 MBA 论文修改最相关的技能重点测试使用</li>
        <li><b>中期（本月）：</b>跟踪论文修改进度，适时调整技能发现关键词策略，提升技能命中率</li>
        <li><b>长期（本季度）：</b>基于 Peter Steinberger 的方法论，建立 Harvey 的自主进化闭环：学习→实践→反馈→优化</li>
    </ul>"""

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
    {next_steps}
    <hr>
    <p style="color:#888;font-size:12px">
        由 Harvey 自动生成 | 四源技能发现系统 | 
        四步学习：Peter Steinberger + OpenClaw 官方<br>
        永久规则 · 不可删除
    </p>
</body></html>"""
    return body

# ── 主流程 ──────────────────────────────────────
def main() -> None:
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


__all__ = ['send_email', 'learn_peter_steinberger', 'learn_openclaw', 'get_new_skills', 'generate_report', 'main']
