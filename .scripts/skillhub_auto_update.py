#!/usr/bin/env python3
"""
SkillHub 技能自动更新脚本
六步流程：每3小时执行一次

步骤细化（James确认版）：
1. 查询 AI智能/智能体、开发工具、效率提升、数据分析、内容创作、通讯协作、安全合规 七大类别 Top100
2. 对比技能库，确认未安装的技能
3. 下载并安装未安装的技能
4. 测试技能：验证功能正常 + 安全性扫描
5. 集成进化系统：验证技能是否成功加载；若失败则取消集成并记录
6. 将结果写入待发送报告（供每日邮件读取）
"""

import subprocess
import json
import os
import urllib.request
import re
import shutil
import smtplib
from datetime import datetime, timezone, timedelta
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ── 配置 ──────────────────────────────────────────
SKILLHUB_INDEX = "https://skillhub-1388575217.cos.ap-guangzhou.myqcloud.com/install/skillhub.md"
SKILLS_DIR     = Path("/Users/fhjtech/.openclaw/workspace/skills")
SKILLS_DB      = Path("/Users/fhjtech/.openclaw/workspace/.learnings/skills_usage.json")
LOG_FILE       = Path("/Users/fhjtech/.openclaw/workspace/.learnings/skill_updates.log")
LOG_MARKER     = Path("/Users/fhjtech/.openclaw/workspace/.learnings/.last_update_summary.json")
SKILLHUB_CMD   = "/Users/fhjtech/.local/bin/skillhub"

# 细化后的七大类别关键词（与 SkillHub 搜索词对应）
CATEGORIES = {
    "AI智能/智能体": ["agent", "ai", "autonomous", "agentic", "gpt", "llm"],
    "开发工具":      ["coding", "developer", "tool", "cli", "ide", "debug"],
    "效率提升":      ["productivity", "workflow", "automation", "task", "schedule"],
    "数据分析":      ["data", "analysis", "analytics", "visualization", "chart"],
    "内容创作":      ["writing", "content", "creative", "blog", "copywriting"],
    "通讯协作":      ["communication", "collab", "team", "chat", "notification"],
    "安全合规":      ["security", "privacy", "compliance", "audit", "auth"],
}

# 邮件配置（每日汇报用）
EMAIL_FROM     = "wcyint@163.com"
EMAIL_TO       = "wcyint@163.com"
EMAIL_PASSWORD  = "NDdE6mZyTMifExXL"
EMAIL_SMTP_HOST = "smtp.163.com"
EMAIL_SMTP_PORT = 465

MAX_INSTALL = 100  # 每次最多安装数量（James确认）

TZ_CST = timezone(timedelta(hours=8))

# ── 日志 ──────────────────────────────────────────
def log(msg):
    ts = datetime.now(TZ_CST).strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line + "\n")

# ── Step 1: 查询七类别 Top100 ────────────────────
def fetch_skills_by_categories():
    all_skills = {}
    for category, keywords in CATEGORIES.items():
        for kw in keywords:
            try:
                result = subprocess.run(
                    [SKILLHUB_CMD, "search", kw],
                    capture_output=True, text=True, timeout=30,
                    cwd=str(SKILLS_DIR.parent)
                )
                if result.returncode != 0:
                    continue
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    stripped = line.strip()
                    if not stripped:
                        continue
                    # 跳过中文行和帮助行
                    if re.match(r'^[\u4e00-\u9fff]', stripped):
                        continue
                    if stripped.startswith('请在机器上') or stripped.startswith('You can use'):
                        continue
                    # 提取 slug（ASCII 字母/数字/短横线/下划线开头）
                    slug_match = re.match(r'^([a-zA-Z0-9_-]+)\s', stripped)
                    if not slug_match:
                        continue
                    slug = slug_match.group(1)
                    rest = stripped[len(slug):].strip()
                    desc = re.sub(r'\s*-\s*version:\s*[\d.]+\s*$', '', rest).strip()
                    ver_match = re.search(r'version:\s*([\d.]+)', stripped)
                    version = ver_match.group(1) if ver_match else ''
                    if slug and slug not in all_skills:
                        all_skills[slug] = {
                            'category': category,
                            'description': desc,
                            'version': version
                        }
            except Exception as e:
                log(f"[Step1] Error searching '{kw}' ({category}): {e}")
    log(f"[Step1] 共获取 {len(all_skills)} 个技能，来自 {len(CATEGORIES)} 大类别")
    return all_skills

# ── Step 2: 对比技能库 ──────────────────────────
def get_installed_skills():
    if not SKILLS_DIR.exists():
        return set()
    return {d.name for d in SKILLS_DIR.iterdir()
            if d.is_dir() and not d.name.startswith('.')}

def find_missing(all_skills):
    installed = get_installed_skills()
    missing = {slug: info for slug, info in all_skills.items()
               if slug not in installed}
    log(f"[Step2] 已安装: {len(installed)} | 缺失: {len(missing)}")
    return missing, installed

# ── Step 3: 下载安装 ──────────────────────────────
def install_skills(missing_skills):
    installed_list, failed_list = [], []
    slugs = list(missing_skills.keys())[:MAX_INSTALL]
    for slug in slugs:
        try:
            log(f"[Step3] Installing: {slug}")
            result = subprocess.run(
                [SKILLHUB_CMD, "install", slug],
                capture_output=True, text=True, timeout=60,
                cwd=str(SKILLS_DIR.parent)
            )
            if result.returncode == 0:
                installed_list.append(slug)
                log(f"[Step3] OK: {slug}")
            else:
                failed_list.append(slug)
                log(f"[Step3] FAIL: {slug} -> {result.stderr[:120]}")
        except Exception as e:
            failed_list.append(slug)
            log(f"[Step3] EXCEPTION: {slug} -> {e}")
    log(f"[Step3] 安装完成: {len(installed_list)} 成功 / {len(failed_list)} 失败")
    return installed_list, failed_list

# ── Step 4: 测试与安全评估 ───────────────────────
def test_and_safety_eval(installed_list):
    """
    安全评估：扫描可疑模式
    功能验证：检查 SKILL.md 是否存在且格式完整
    """
    safe_list, unsafe_list = [], []
    SUSPICIOUS = [
        "curl ", "wget ", "rm -rf /", "chmod 777",
        "eval $", "exec ", "base64 -d",
        "os.system(", "subprocess.call",
        ".send(", "http.request(",
        "process.env", "os.environ",
    ]
    for slug in installed_list:
        skill_path = SKILLS_DIR / slug
        if not skill_path.exists():
            unsafe_list.append((slug, "目录不存在"))
            continue
        # 功能检查：SKILL.md 必须存在
        skill_md = skill_path / "SKILL.md"
        if not skill_md.exists():
            log(f"[Step4] WARN: {slug} 无 SKILL.md")
        else:
            # 基本格式检查：至少有 description 和 when to use
            try:
                content = skill_md.read_text(encoding='utf-8', errors='ignore')
                if len(content) < 50:
                    log(f"[Step4] WARN: {slug} SKILL.md 内容过短 ({len(content)} chars)")
            except Exception as e:
                log(f"[Step4] WARN: {slug} SKILL.md 读取失败: {e}")
        # 安全扫描
        is_safe = True
        reason = ""
        try:
            for py_file in skill_path.rglob("*.py"):
                c = py_file.read_text(encoding='utf-8', errors='ignore')
                for pat in SUSPICIOUS:
                    if pat in c:
                        is_safe = False
                        reason = f"pattern '{pat}' in {py_file.name}"
                        break
            for js_file in skill_path.rglob("*.js"):
                c = js_file.read_text(encoding='utf-8', errors='ignore')
                for pat in SUSPICIOUS:
                    if pat in c:
                        is_safe = False
                        reason = f"pattern '{pat}' in {js_file.name}"
                        break
        except Exception as e:
            log(f"[Step4] ERROR scanning {slug}: {e}")
        if is_safe:
            safe_list.append(slug)
        else:
            unsafe_list.append((slug, reason))
            log(f"[Step4] UNSAFE: {slug} -> {reason}")
    log(f"[Step4] 安全通过: {len(safe_list)} | 危险: {len(unsafe_list)}")
    return safe_list, unsafe_list

# ── Step 5: 集成进化系统 + 验证 ──────────────────
def integrate_and_verify(safe_list, all_skills):
    """
    尝试将技能接入 OpenClaw 进化系统（写入 skills/ 目录的活跃状态）
    若 SKILL.md 加载失败或格式异常，撤销安装并记录
    """
    integrated_ok, integration_failed = [], []
    for slug in safe_list:
        skill_path = SKILLS_DIR / slug
        skill_md = skill_path / "SKILL.md"
        try:
            # 验证 SKILL.md 可正常读取（模拟 OpenClaw 加载）
            content = skill_md.read_text(encoding='utf-8', errors='ignore')
            if len(content) < 50:
                raise ValueError(f"SKILL.md too short: {len(content)} chars")
            # 写入活跃标记
            status_file = skill_path / ".active"
            status_file.write_text(
                json.dumps({"integrated_at": datetime.now(TZ_CST).isoformat(),
                            "status": "active"}, indent=2)
            )
            integrated_ok.append(slug)
            log(f"[Step5] OK: {slug} integrated and verified")
        except Exception as e:
            # 撤销：删除安装目录
            log(f"[Step5] FAIL: {slug} -> {e}，撤销安装")
            try:
                shutil.rmtree(skill_path)
                log(f"[Step5] Reverted: {slug}")
            except Exception as re:
                log(f"[Step5] Revert failed for {slug}: {re}")
            integration_failed.append((slug, str(e)))
    log(f"[Step5] 集成成功: {len(integrated_ok)} | 失败撤销: {len(integration_failed)}")
    return integrated_ok, integration_failed

# ── Step 6: 更新数据库 + 写待发报告 ──────────────
def finalize(integrated_ok, all_skills):
    # 更新 skills_usage.json
    try:
        with open(SKILLS_DB, 'r') as f:
            data = json.load(f)
    except:
        data = {"skills": {}, "categories": {}, "total_uses": 0}
    today = datetime.now(TZ_CST).strftime("%Y-%m-%d")
    for slug in integrated_ok:
        info = all_skills.get(slug, {})
        if slug not in data["skills"]:
            data["skills"][slug] = {
                "count": 0, "first_used": None,
                "contexts": [], "last_used": None,
                "description": info.get("description", ""),
                "category": info.get("category", ""),
                "status": "auto-installed",
                "installed_date": today,
                "version": info.get("version", "")
            }
    with open(SKILLS_DB, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    # 写待发送报告（供每日汇报脚本读取并发送邮件）
    summary = {
        "date": today,
        "skills": [
            {"slug": s, "description": all_skills.get(s, {}).get("description", ""),
             "category": all_skills.get(s, {}).get("category", "")}
            for s in integrated_ok
        ]
    }
    with open(LOG_MARKER, 'w') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    log(f"[Step6] 完成: {len(integrated_ok)} 个技能已集成")

# ── 主流程 ────────────────────────────────────────
def main():
    log("=== SkillHub Auto-Update Started ===")
    # Step 1
    all_skills = fetch_skills_by_categories()
    if not all_skills:
        log("[Step1] 无技能获取，中止")
        return
    # Step 2
    missing, _ = find_missing(all_skills)
    if not missing:
        log("所有技能已是最新")
        return
    # Step 3
    newly_installed, install_failed = install_skills(missing)
    if not newly_installed:
        log("[Step3] 无新安装技能，中止")
        return
    # Step 4
    safe_list, unsafe_list = test_and_safety_eval(newly_installed)
    if not safe_list:
        log("[Step4] 无安全技能，中止")
        return
    # Step 5
    integrated_ok, integration_failed = integrate_and_verify(safe_list, all_skills)
    # Step 6
    finalize(integrated_ok, all_skills)
    log(f"=== 完成: 集成{len(integrated_ok)} | 安全{len(safe_list)} | 安装{len(newly_installed)} | 失败{len(install_failed)} ===")

if __name__ == "__main__":
    main()
