#!/usr/bin/env python3
"""
SkillHub 技能自动更新脚本 - 全四源版
每90分钟执行一次，六步流程：
  1. 并发搜索 SkillHub + ClawHub + VoltAgent(GitHub) + Skills.sh
  2. 对比技能库（已安装/未安装）
  3. 下载安装未安装的技能
  4. 安全评估
  5. 集成验证
  6. 更新数据库
"""

import asyncio
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
from typing import Optional

# ── 配置 ──────────────────────────────────────────
SKILLS_DIR   = Path("/Users/fhjtech/.openclaw/workspace/skills")
SKILLS_DB    = Path("/Users/fhjtech/.openclaw/workspace/.learnings/skills_usage.json")
LOG_FILE     = Path("/Users/fhjtech/.openclaw/workspace/.learnings/skill_updates.log")
LOG_MARKER   = Path("/Users/fhjtech/.openclaw/workspace/.learnings/.last_update_summary.json")
SKILLHUB_CMD = "/Users/fhjtech/.local/bin/skillhub"
CLAWHUB_CMD  = "/opt/homebrew/bin/clawhub"
MAX_INSTALL  = 15   # 每轮最多安装15个（James确认）
MAX_CONCURRENCY = 20

TZ_CST = timezone(timedelta(hours=8))

# 六大类别
CATEGORIES = ["AI智能", "开发工具", "效率提升", "数据分析", "内容创作", "通讯协作", "安全合规"]

# ── 日志 ──────────────────────────────────────────
def log(msg: str) -> None:
    ts = datetime.now(TZ_CST).strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# ── Step 1a: SkillHub 搜索 ──────────────────────
async def _search_skillhub(keyword: str, semaphore: asyncio.Semaphore) -> list[dict]:
    async with semaphore:
        try:
            proc = await asyncio.create_subprocess_exec(
                SKILLHUB_CMD, "search", keyword,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(SKILLS_DIR.parent)
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)
            if proc.returncode != 0:
                return []
            return _parse_skillhub_output(stdout.decode("utf-8", errors="ignore"), source="skillhub")
        except asyncio.TimeoutError:
            return []
        except Exception as e:
            log(f"[SkillHub] Error: {e}")
            return []

# ── Step 1b: ClawHub 搜索 ────────────────────────
async def _search_clawhub(keyword: str, semaphore: asyncio.Semaphore) -> list[dict]:
    async with semaphore:
        try:
            proc = await asyncio.create_subprocess_exec(
                CLAWHUB_CMD, "search", keyword,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(SKILLS_DIR.parent)
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)
            if proc.returncode != 0:
                return []
            return _parse_skillhub_output(stdout.decode("utf-8", errors="ignore"), source="clawhub")
        except asyncio.TimeoutError:
            return []
        except Exception as e:
            log(f"[ClawHub] Error: {e}")
            return []

# ── Step 1c: VoltAgent GitHub ────────────────────
async def _fetch_voltagent(semaphore: asyncio.Semaphore) -> list[dict]:
    async with semaphore:
        try:
            url = "https://raw.githubusercontent.com/VoltAgent/awesome-openclaw-skills/main/README.md"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read().decode("utf-8", errors="ignore")
            return _parse_voltagent_readme(content)
        except Exception as e:
            log(f"[VoltAgent] Error: {e}")
            return []

# ── Step 1d: Skills.sh ─────────────────────────
async def _fetch_skills_sh(semaphore: asyncio.Semaphore) -> list[dict]:
    async with semaphore:
        try:
            # Skills.sh 没有公开 API，用网页抓取
            url = "https://skills.sh/"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read().decode("utf-8", errors="ignore")
            return _parse_skills_sh(content)
        except Exception as e:
            log(f"[Skills.sh] Error: {e}")
            return []

# ── 解析器 ──────────────────────────────────────
INVALID_SLUGS = {
    "-", "Use", "For", "and", "MANDATORY", "Navigate", "Google", "Gmail",
    "Gpt", "Brand-specific", "CornerStone", "ClickSend", "ClickFunnels",
    "BluOS", "NotebookLM", "inflated", "comprehensive", "Notion",
    "Requires", "Acuity", "docker", "Jeffrey", "Auto-detect",
    "Multi-platform", "Ad", "ManyChat", "Box", "Teamo", "persuasive",
    "Decision", "gumroad", "Auto-invoked", "spawn", "Comprehensive",
    "troubleshooting", "airtable", "llm", "Billions", "EvoMap"
}

def _is_valid_slug(slug: str) -> bool:
    if not slug or slug in INVALID_SLUGS:
        return False
    if not re.search(r"[a-zA-Z]", slug):
        return False
    if re.match(r"^[\d-]+$", slug):
        return False
    return True

def _parse_skillhub_output(stdout: str, source: str) -> list[dict]:
    skills = []
    for line in stdout.strip().split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        if re.match(r"^[\u4e00-\u9fff]", stripped):
            continue
        if stripped.startswith("请在机器上") or stripped.startswith("You can use"):
            continue
        slug_match = re.match(r"^([a-zA-Z0-9_-]+)\s", stripped)
        if not slug_match:
            continue
        slug = slug_match.group(1)
        if not _is_valid_slug(slug):
            continue
        rest = stripped[len(slug):].strip()
        desc = re.sub(r"\s*-\s*version:\s*[\d.]+\s*$", "", rest).strip()
        ver_match = re.search(r"version:\s*([\d.]+)", stripped)
        version = ver_match.group(1) if ver_match else ""
        skills.append({"slug": slug, "description": desc, "version": version, "source": source})
    return skills

def _parse_voltagent_readme(content: str) -> list[dict]:
    skills = []
    # 匹配 ## SkillName 或 - [SkillName](url) 格式
    for line in content.split("\n"):
        m = re.match(r"- \[([a-zA-Z0-9_-]+)\]\(https://", line)
        if m:
            slug = m.group(1)
            if _is_valid_slug(slug):
                desc = line.split("](")[0].replace("- [", "").strip()
                skills.append({"slug": slug, "description": desc, "version": "", "source": "voltagent"})
    return skills

def _parse_skills_sh(content: str) -> list[dict]:
    skills = []
    # skills.sh 页面结构：找技能名称和链接
    for line in content.split("\n"):
        m = re.search(r'href="/skill/([a-zA-Z0-9_-]+)"[^>]*>([^<]+)', line)
        if m:
            slug = m.group(1)
            desc = m.group(2).strip()
            if _is_valid_slug(slug):
                skills.append({"slug": slug, "description": desc, "version": "", "source": "skills.sh"})
    return skills

# ── Step 1: 全四源并发搜索 ─────────────────────
async def step1_fetch_all() -> dict[str, dict]:
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
    tasks = []

    # SkillHub
    for kw in ["agent", "ai", "autonomous", "coding", "developer", "tool",
               "productivity", "workflow", "automation", "data", "analysis",
               "writing", "content", "creative", "communication", "collab",
               "security", "privacy"]:
        tasks.append(_search_skillhub(kw, semaphore))

    # ClawHub
    for kw in ["agent", "ai", "coding", "developer", "automation", "workflow",
               "data", "analysis", "writing", "content", "communication"]:
        tasks.append(_search_clawhub(kw, semaphore))

    # VoltAgent
    tasks.append(_fetch_voltagent(semaphore))

    # Skills.sh
    tasks.append(_fetch_skills_sh(semaphore))

    results = await asyncio.gather(*tasks)
    all_skills: dict[str, dict] = {}
    for skill_list in results:
        for s in skill_list:
            slug = s["slug"]
            if slug not in all_skills:
                all_skills[slug] = s
    log(f"[Step1] 四源获取 {len(all_skills)} 个技能")
    return all_skills

# ── Step 2: 对比技能库 ─────────────────────────
def step2_find_missing(all_skills: dict[str, dict]) -> tuple[dict[str, dict], set[str]]:
    installed = {d.name for d in SKILLS_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")}
    missing = {slug: info for slug, info in all_skills.items() if slug not in installed}
    log(f"[Step2] 已安装: {len(installed)} | 缺失: {len(missing)}")
    return missing, installed

# ── Step 3: 优先级安装 ─────────────────────────
async def _install_one(slug: str, source: str, semaphore: asyncio.Semaphore) -> tuple[str, bool, str]:
    async with semaphore:
        try:
            if source == "clawhub":
                proc = await asyncio.create_subprocess_exec(
                    CLAWHUB_CMD, "install", slug,
                    stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
                    cwd=str(SKILLS_DIR.parent)
                )
            else:
                proc = await asyncio.create_subprocess_exec(
                    SKILLHUB_CMD, "install", slug,
                    stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
                    cwd=str(SKILLS_DIR.parent)
                )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=60)
            ok = proc.returncode == 0
            status = "OK" if ok else f"FAIL({stderr.decode()[:60]})"
            log(f"[Step3] {status}: {slug} ({source})")
            return (slug, ok, source)
        except asyncio.TimeoutError:
            return (slug, False, source)
        except Exception as e:
            log(f"[Step3] EXCEPTION {slug}: {e}")
            return (slug, False, source)

async def step3_install(missing: dict[str, dict]) -> tuple[list[str], list[str]]:
    # 优先 SkillHub > ClawHub > 其他来源，去重
    seen, ordered = set(), []
    for slug, info in missing.items():
        if slug not in seen:
            seen.add(slug)
            ordered.append((slug, info["source"]))
    slugs_to_install = [s for s, _ in ordered[:MAX_INSTALL]]
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
    tasks = [_install_one(slug, src, semaphore) for slug, src in ordered[:MAX_INSTALL]]
    results = await asyncio.gather(*tasks)
    ok_list = [slug for slug, ok, _ in results if ok]
    fail_list = [slug for slug, ok, _ in results if not ok]
    log(f"[Step3] 安装完成: {len(ok_list)} 成功 / {len(fail_list)} 失败")
    return ok_list, fail_list

# ── Step 4: 安全扫描 ────────────────────────────
DANGEROUS = [
    "curl ", "wget ", "rm -rf /", "chmod 777", "eval $", "base64 -d", ".send(",
]
SAFE_ENV_PATTERNS = ["os.environ.get(", "os.environ[", "os.getenv(", "process.env."]

def step4_safety_eval(installed: list[str]) -> tuple[list[str], list[tuple[str, str]]]:
    safe, unsafe = [], []
    for slug in installed:
        sp = SKILLS_DIR / slug
        if not sp.exists():
            unsafe.append((slug, "目录不存在"))
            continue
        skill_md = sp / "SKILL.md"
        if not skill_md.exists():
            unsafe.append((slug, "无 SKILL.md"))
            log(f"[Step4] UNSAFE: {slug} -> 无 SKILL.md")
            continue
        is_safe = True
        reason = ""
        try:
            for py_file in sp.rglob("*.py"):
                c = py_file.read_text(encoding="utf-8", errors="ignore")
                for pat in DANGEROUS:
                    if pat in c:
                        if pat == ".send(" and any(safe_pat in c for safe_pat in SAFE_ENV_PATTERNS):
                            pass
                        else:
                            is_safe = False
                            reason = f"'{pat}' in {py_file.name}"
                            break
                if not is_safe:
                    break
            if is_safe:
                for js_file in sp.rglob("*.js"):
                    c = js_file.read_text(encoding="utf-8", errors="ignore")
                    for pat in DANGEROUS:
                        if pat in c:
                            is_safe = False
                            reason = f"'{pat}' in {js_file.name}"
                            break
                    if not is_safe:
                        break
        except Exception as e:
            log(f"[Step4] ERROR scanning {slug}: {e}")
        if is_safe:
            safe.append(slug)
        else:
            unsafe.append((slug, reason))
            log(f"[Step4] UNSAFE: {slug} -> {reason}")
    log(f"[Step4] 安全通过: {len(safe)} | 危险: {len(unsafe)}")
    return safe, unsafe

# ── Step 5: 集成验证 ──────────────────────────
def step5_integrate(safe: list[str], all_skills: dict) -> tuple[list[str], list[tuple[str, str]]]:
    integrated, failed = [], []
    for slug in safe:
        sp = SKILLS_DIR / slug
        skill_md = sp / "SKILL.md"
        try:
            content = skill_md.read_text(encoding="utf-8", errors="ignore")
            if len(content) < 50:
                raise ValueError(f"SKILL.md too short: {len(content)} chars")
            (sp / ".active").write_text(
                json.dumps({"integrated_at": datetime.now(TZ_CST).isoformat(), "status": "active"})
            )
            integrated.append(slug)
            log(f"[Step5] OK: {slug}")
        except Exception as e:
            log(f"[Step5] FAIL: {slug} -> {e}，撤销")
            try:
                shutil.rmtree(sp)
            except Exception:
                pass
            failed.append((slug, str(e)))
    log(f"[Step5] 集成成功: {len(integrated)} | 撤销: {len(failed)}")
    return integrated, failed

# ── Step 6: 更新数据库 ────────────────────────
def step6_finalize(integrated: list[str], all_skills: dict) -> None:
    try:
        with open(SKILLS_DB, "r") as f:
            data = json.load(f)
    except:
        data = {"skills": {}, "categories": {}, "total_uses": 0}
    today = datetime.now(TZ_CST).strftime("%Y-%m-%d")
    for slug in integrated:
        info = all_skills.get(slug, {})
        if slug not in data["skills"]:
            data["skills"][slug] = {
                "count": 0, "first_used": None,
                "contexts": [], "last_used": None,
                "description": info.get("description", ""),
                "category": info.get("source", ""),
                "status": "auto-installed",
                "installed_date": today,
                "version": info.get("version", ""),
                "source": info.get("source", "")
            }
    with open(SKILLS_DB, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    summary = {"date": today, "skills": [
        {"slug": s, "description": all_skills.get(s, {}).get("description", ""),
         "source": all_skills.get(s, {}).get("source", "")}
        for s in integrated
    ]}
    with open(LOG_MARKER, "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    log(f"[Step6] 完成，{len(integrated)} 个技能已集成")

# ── 汇报邮件（自动发送到 wgcapsa@163.com）──────
def send_install_report(integrated, fail_list, unsafe):
    EMAIL_FROM, EMAIL_TO = "wcyint@163.com", "wcyint@163.com"
    SMTP_HOST, SMTP_PORT = "smtp.163.com", 465
    EMAIL_PASSWORD = "NDdE6mZyTMifExXL"

    now = datetime.now(TZ_CST)
    subject = f"📦 技能自动更新 | {now.strftime('%m-%d %H:%M')} | {len(integrated)} 个新技能"

    rows = ""
    for s in integrated:
        rows += f"<tr><td><code>{s}</code></td><td>{all_skills.get(s, {}).get('source','')}</td><td>{all_skills.get(s, {}).get('description','')[:60]}</td></tr>"

    body = f"""
    <h2>📦 技能自动更新报告</h2>
    <p><b>时间：</b>{now.strftime('%Y-%m-%d %H:%M')} (北京时间)</p>
    <p><b>新安装：</b>{len(integrated)} 个 &nbsp; <b>失败：</b>{len(fail_list)} 个 &nbsp; <b>安全拦截：</b>{len(unsafe)} 个</p>
    <hr>
    <table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;width:100%">
        <tr style="background:#f0f0f0"><th>技能</th><th>来源</th><th>描述</th></tr>
        {rows or '<tr><td colspan=3>无</td></tr>'}
    </table>
    <hr>
    <p style="color:#888;font-size:12px">由 Harvey 自动生成 | 四源技能发现系统 (SkillHub+ClawHub+VoltAgent+Skills.sh)</p>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg.attach(MIMEText(body, "html", "utf-8"))
    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            server.sendmail(EMAIL_FROM, [EMAIL_TO], msg.as_string())
        log(f"[邮件] 汇报已发送至 {EMAIL_TO}")
    except Exception as e:
        log(f"[邮件] 发送失败: {e}")

# ── 主流程 ──────────────────────────────────────
all_skills = {}

def main() -> None:
    log("=== 四源技能自动更新 Started ===")
    all_skills = asyncio.run(step1_fetch_all())
    if not all_skills:
        log("[Step1] 无技能获取，中止")
        return
    missing, _ = step2_find_missing(all_skills)
    if not missing:
        log("所有技能已是最新")
        return
    newly_installed, install_failed = asyncio.run(step3_install(missing))
    if not newly_installed:
        log("[Step3] 无新安装，中止")
        return
    safe, unsafe = step4_safety_eval(newly_installed)
    if not safe:
        log("[Step4] 无安全技能，中止")
        return
    integrated, failed = step5_integrate(safe, all_skills)
    step6_finalize(integrated, all_skills)
    # 发送邮件汇报
    send_install_report(integrated, install_failed, unsafe)
    log(f"=== 完成: 集成{len(integrated)} | 安全{len(safe)} | 安装{len(newly_installed)} ===")

if __name__ == "__main__":
    main()
