#!/usr/bin/env python3
"""
SkillHub 技能自动更新脚本 - asyncio 并发版
六步流程：每3小时执行一次

性能改进（Level 1 → Level 2）：
- Step1: asyncio 并发搜索所有类别关键词（原来串行60s → 并发约5s）
- Step3: asyncio.Semaphore 控制并发安装（避免API限流）
- 全面加入 type hints
"""

import asyncio
import subprocess
import json
import os
import urllib.request
import re
import shutil
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
MAX_INSTALL  = 100
MAX_CONCURRENCY = 20  # 并发控制

TZ_CST = timezone(timedelta(hours=8))

# 细化后的七大类别关键词
CATEGORIES: dict[str, list[str]] = {
    "AI智能/智能体": ["agent", "ai", "autonomous", "agentic", "gpt", "llm"],
    "开发工具":      ["coding", "developer", "tool", "cli", "ide", "debug"],
    "效率提升":      ["productivity", "workflow", "automation", "task", "schedule"],
    "数据分析":      ["data", "analysis", "analytics", "visualization", "chart"],
    "内容创作":      ["writing", "content", "creative", "blog", "copywriting"],
    "通讯协作":      ["communication", "collab", "team", "chat", "notification"],
    "安全合规":      ["security", "privacy", "compliance", "audit", "auth"],
}

# ── 日志 ──────────────────────────────────────────
def log(msg: str) -> None:
    ts = datetime.now(TZ_CST).strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# ── Step 1: asyncio 并发搜索 ────────────────────
async def _search_one(keyword: str, semaphore: asyncio.Semaphore) -> tuple[str, list[dict]]:
    """搜索单个关键词，返回 (keyword, skills_list)"""
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
                return (keyword, [])
            return (keyword, _parse_skillhub_output(stdout.decode("utf-8", errors="ignore")))
        except asyncio.TimeoutError:
            return (keyword, [])
        except Exception as e:
            log(f"[Step1] Error searching '{keyword}': {e}")
            return (keyword, [])

def _parse_skillhub_output(stdout: str) -> list[dict]:
    """解析 skillhub search 输出"""
    skills: list[dict] = []
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
        rest = stripped[len(slug):].strip()
        desc = re.sub(r"\s*-\s*version:\s*[\d.]+\s*$", "", rest).strip()
        ver_match = re.search(r"version:\s*([\d.]+)", stripped)
        version = ver_match.group(1) if ver_match else ""
        skills.append({"slug": slug, "description": desc, "version": version})
    return skills

async def step1_fetch_all() -> dict[str, dict]:
    """并发搜索所有类别关键词"""
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
    tasks = []
    for category, keywords in CATEGORIES.items():
        for kw in keywords:
            tasks.append(_search_one(kw, semaphore))
    results = await asyncio.gather(*tasks)
    all_skills: dict[str, dict] = {}
    for keyword, skills in results:
        for s in skills:
            slug = s["slug"]
            if slug not in all_skills:
                all_skills[slug] = {
                    "category": keyword,  # 用关键词作为分类
                    "description": s["description"],
                    "version": s["version"],
                }
    log(f"[Step1] 并发获取 {len(all_skills)} 个技能")
    return all_skills

# ── Step 2: 对比技能库 ──────────────────────────
def step2_find_missing(all_skills: dict[str, dict]) -> tuple[dict[str, dict], set[str]]:
    installed = {d.name for d in SKILLS_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")}
    missing = {slug: info for slug, info in all_skills.items() if slug not in installed}
    log(f"[Step2] 已安装: {len(installed)} | 缺失: {len(missing)}")
    return missing, installed

# ── Step 3: asyncio 并发安装 ────────────────────
async def _install_one(slug: str, semaphore: asyncio.Semaphore) -> tuple[str, bool]:
    async with semaphore:
        try:
            proc = await asyncio.create_subprocess_exec(
                SKILLHUB_CMD, "install", slug,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(SKILLS_DIR.parent)
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=60)
            ok = proc.returncode == 0
            status = "OK" if ok else f"FAIL({stderr.decode()[:60]})"
            log(f"[Step3] {status}: {slug}")
            return (slug, ok)
        except asyncio.TimeoutError:
            return (slug, False)
        except Exception as e:
            log(f"[Step3] EXCEPTION {slug}: {e}")
            return (slug, False)

async def step3_install(missing: dict[str, dict]) -> tuple[list[str], list[str]]:
    slugs = list(missing.keys())[:MAX_INSTALL]
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
    tasks = [_install_one(slug, semaphore) for slug in slugs]
    results = await asyncio.gather(*tasks)
    ok_list = [slug for slug, ok in results if ok]
    fail_list = [slug for slug, ok in results if not ok]
    log(f"[Step3] 安装完成: {len(ok_list)} 成功 / {len(fail_list)} 失败")
    return ok_list, fail_list

# ── Step 4: 安全扫描 ─────────────────────────────
def step4_safety_eval(installed: list[str]) -> tuple[list[str], list[tuple[str, str]]]:
    SUSPICIOUS = ["curl ", "wget ", "rm -rf /", "chmod 777",
                  "eval $", "exec ", "base64 -d",
                  "os.system(", "subprocess.call(",
                  ".send(", "http.request(", "process.env", "os.environ"]
    safe, unsafe = [], []
    for slug in installed:
        sp = SKILLS_DIR / slug
        if not sp.exists():
            unsafe.append((slug, "目录不存在"))
            continue
        skill_md = sp / "SKILL.md"
        if not skill_md.exists():
            log(f"[Step4] WARN: {slug} 无 SKILL.md")
        is_safe = True
        reason = ""
        try:
            for py_file in sp.rglob("*.py"):
                c = py_file.read_text(encoding="utf-8", errors="ignore")
                for pat in SUSPICIOUS:
                    if pat in c:
                        is_safe = False
                        reason = f"'{pat}' in {py_file.name}"
                        break
            for js_file in sp.rglob("*.js"):
                c = js_file.read_text(encoding="utf-8", errors="ignore")
                for pat in SUSPICIOUS:
                    if pat in c:
                        is_safe = False
                        reason = f"'{pat}' in {js_file.name}"
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

# ── Step 5: 集成验证 ─────────────────────────────
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

# ── Step 6: 更新数据库 ──────────────────────────
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
                "category": info.get("category", ""),
                "status": "auto-installed",
                "installed_date": today,
                "version": info.get("version", "")
            }
    with open(SKILLS_DB, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    summary = {"date": today, "skills": [
        {"slug": s, "description": all_skills.get(s, {}).get("description", ""),
         "category": all_skills.get(s, {}).get("category", "")}
        for s in integrated
    ]}
    with open(LOG_MARKER, "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    log(f"[Step6] 完成，{len(integrated)} 个技能已集成")

# ── 主流程 ────────────────────────────────────────
def main() -> None:
    log("=== SkillHub Auto-Update (async) Started ===")
    # Step 1: asyncio并发获取
    all_skills = asyncio.run(step1_fetch_all())
    if not all_skills:
        log("[Step1] 无技能获取，中止")
        return
    # Step 2
    missing, _ = step2_find_missing(all_skills)
    if not missing:
        log("所有技能已是最新")
        return
    # Step 3: asyncio并发安装
    newly_installed, install_failed = asyncio.run(step3_install(missing))
    if not newly_installed:
        log("[Step3] 无新安装，中止")
        return
    # Step 4
    safe, unsafe = step4_safety_eval(newly_installed)
    if not safe:
        log("[Step4] 无安全技能，中止")
        return
    # Step 5
    integrated, failed = step5_integrate(safe, all_skills)
    # Step 6
    step6_finalize(integrated, all_skills)
    log(f"=== 完成: 集成{len(integrated)} | 安全{len(safe)} | 安装{len(newly_installed)} | 失败{len(install_failed)} ===")

if __name__ == "__main__":
    main()
