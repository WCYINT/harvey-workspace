#!/usr/bin/env python3
"""
Harvey 主动预见进化任务
空闲检测 + 主动分析 + 自我修复

触发条件：
  - 30分钟无人类消息时启动
  - 检测论文上下文逻辑断层
  - 检测cron任务健康状态
  - 检测API使用率
  - 发现问题主动修复或汇报
"""

import json, os, smtplib
from datetime import datetime, timezone, timedelta
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

TZ_CST = timezone(timedelta(hours=8))
NOW = datetime.now(TZ_CST)
LOG_DIR = Path("/Users/fhjtech/.openclaw/workspace/.learnings")
IDLE_MARKER = LOG_DIR / ".last_human_message.json"
EVOLUTION_LOG = LOG_DIR / "proactive_evolution.json"
SKILLS_DIR = Path("/Users/fhjtech/.openclaw/workspace/skills")

# 发送主动汇报邮件
def send_alert(subject: str, body: str):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = "wcyint@163.com"
        msg["To"] = "wcyint@163.com"
        msg.attach(MIMEText(body, "html", "utf-8"))
        with smtplib.SMTP_SSL("smtp.163.com", 465) as s:
            s.login("wcyint@163.com", "NDdE6mZyTMifExXL")
            s.sendmail("wcyint@163.com", ["wcyint@163.com"], msg.as_string())
        return True
    except:
        return False

# 检测最后人类消息时间
def check_idle_minutes() -> int:
    try:
        if IDLE_MARKER.exists():
            data = json.loads(IDLE_MARKER.read_text())
            last = datetime.fromisoformat(data["timestamp"])
            return int((datetime.now(TZ_CST) - last).total_seconds() / 60)
    except:
        pass
    return 999  # 无记录，默认空闲

# 主动检测1：论文上下文逻辑（如果论文文件存在）
def check_thesis_logic() -> dict:
    issues = []
    try:
        thesis_path = Path("/Volumes/10-ShareData/0-Thesis/最后一版")
        if thesis_path.exists():
            latest = max(thesis_path.glob("*.docm"), key=lambda p: p.stat().st_mtime, default=None)
            if latest:
                age_hours = (datetime.now(TZ_CST) - datetime.fromtimestamp(latest.stat().st_mtime, TZ_CST)).total_seconds() / 3600
                if age_hours > 24:
                    issues.append(f"论文已{age_hours:.0f}小时未更新，可能需要确认修改进度")
    except Exception as e:
        issues.append(f"论文检查异常: {e}")
    return {"module": "thesis_logic", "status": "ok" if not issues else "warning", "issues": issues}

# 主动检测2：cron任务健康状态
def check_cron_health() -> dict:
    issues = []
    status_map = {"ok": 0, "error": 0}
    try:
        import subprocess
        result = subprocess.run(
            ["/Users/fhjtech/.nvm/versions/node/v24.13.1/bin/openclaw", "cron", "list"],
            capture_output=True, text=True, timeout=15
        )
        for line in result.stdout.split('\n'):
            if 'error' in line.lower():
                status_map["error"] += 1
            elif 'ok' in line.lower():
                status_map["ok"] += 1
        if status_map["error"] > 2:
            issues.append(f"有{status_map['error']}个cron任务error，建议检查")
    except Exception as e:
        issues.append(f"cron检查异常: {e}")
    return {"module": "cron_health", "status": "warning" if issues else "ok", "issues": issues, "stats": status_map}

# 主动检测3：API使用率（如果可读）
def check_api_usage() -> dict:
    issues = []
    try:
        import subprocess
        result = subprocess.run(
            ["/Users/fhjtech/.nvm/versions/node/v24.13.1/bin/openclaw", "cron", "list"],
            capture_output=True, text=True, timeout=10
        )
        # 检查minimax-usage-monitor状态
        if "minimax" in result.stdout.lower() and "error" in result.stdout.lower():
            issues.append("MiniMax usage monitor可能异常，建议手动检查")
    except:
        pass
    return {"module": "api_usage", "status": "ok" if not issues else "warning", "issues": issues}

# 主动检测4：技能协同分析（检查最近安装的技能是否有协同可能）
def check_skill_synergy() -> dict:
    issues = []
    try:
        installed = sorted([d.name for d in SKILLS_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")])
        # 检查是否有明显的技能协同缺失
        has_analysis = any("data" in s or "analysis" in s or "stat" in s for s in installed)
        has_viz = any("plot" in s or "chart" in s or "viz" in s or "visual" in s for s in installed)
        if has_analysis and not has_viz:
            issues.append("有数据分析技能但缺少可视化技能，建议安装python-dataviz或类似技能")
        if has_analysis and not any("doe" in s or "regression" in s or "ml" in s for s in installed):
            issues.append("有分析技能但缺少DOE/ML技能，可能影响论文数据分析能力")
    except Exception as e:
        issues.append(f"技能协同检查异常: {e}")
    return {"module": "skill_synergy", "status": "ok" if not issues else "info", "issues": issues}

# 主动检测5：最近进化记录复盘
def check_evolution_progress() -> dict:
    issues = []
    try:
        records = []
        if EVOLUTION_LOG.exists():
            records = json.loads(EVOLUTION_LOG.read_text())
        recent = [r for r in records if datetime.fromisoformat(r.get("timestamp", "2000")).total_seconds() > 86400]  # 24h内
        if len(recent) < 3:
            issues.append(f"过去24小时仅{len(recent)}次进化记录，可能进化不充分")
    except:
        pass
    return {"module": "evolution_progress", "status": "ok" if not issues else "info", "issues": issues}

def main():
    print(f"[{NOW.strftime('%H:%M:%S')}] === 主动预见进化 Started ===")

    idle_mins = check_idle_minutes()
    print(f"[空闲检测] {idle_mins}分钟无人类消息")

    if idle_mins < 30:
        print(f"[跳过] 空闲仅{idle_mins}分钟(<30)，不触发主动进化")
        return

    # 执行主动检测
    results = [
        check_thesis_logic(),
        check_cron_health(),
        check_api_usage(),
        check_skill_synergy(),
        check_evolution_progress(),
    ]

    # 汇总问题
    all_issues = []
    for r in results:
        all_issues.extend(r.get("issues", []))

    if not all_issues:
        print(f"[主动预见] 所有检测正常，无主动动作")
        return

    # 生成汇报
    issue_items = "".join(f"<li>{i}</li>" for i in all_issues)
    body = f"""
    <h2>🔔 Harvey 主动预见报告</h2>
    <p><b>时间：</b>{NOW.strftime('%Y-%m-%d %H:%M')} (北京时间)</p>
    <p><b>触发条件：</b>空闲{idle_mins}分钟后自动检测</p>
    <hr>
    <h3>发现以下事项：</h3>
    <ol>{issue_items}</ol>
    <hr>
    <p><b>检测模块：</b>论文逻辑 | Cron健康 | API状态 | 技能协同 | 进化进度</p>
    """
    subject = f"🔔 主动预见：{len(all_issues)}个事项待处理 | {NOW.strftime('%H:%M')}"
    sent = send_alert(subject, body)
    print(f"[主动预见] 发现{len(all_issues)}个事项，邮件发送{'成功' if sent else '失败'}")
    for i in all_issues:
        print(f"  - {i}")

    # 记录
    try:
        records = json.loads(EVOLUTION_LOG.read_text()) if EVOLUTION_LOG.exists() else []
        records.append({
            "timestamp": NOW.isoformat(),
            "idle_mins": idle_mins,
            "issues": all_issues,
            "results": results
        })
        EVOLUTION_LOG.write_text(json.dumps(records[-100:], indent=2))  # 保留最近100条
    except:
        pass

if __name__ == "__main__":
    main()
