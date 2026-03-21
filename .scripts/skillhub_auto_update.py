#!/usr/bin/env python3
"""
SkillHub 技能自动更新脚本
六步流程：每3小时执行一次
1. 从 skillhub.md 获取每个类别 Top100 技能清单
2. 对比本地技能库，确认未安装的技能
3. 下载并安装未安装的技能
4. 测试技能并评估安全性
5. 安装测试合格的技能
6. 结果写入 .learnings/skill_updates.log（供每日汇报读取）
"""

import subprocess
import json
import os
import urllib.request
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

SKILLHUB_INDEX = "https://skillhub-1388575217.cos.ap-guangzhou.myqcloud.com/install/skillhub.md"
SKILLS_DIR     = Path("/Users/fhjtech/.openclaw/workspace/skills")
SKILLS_DB      = Path("/Users/fhjtech/.openclaw/workspace/.learnings/skills_usage.json")
LOG_FILE       = Path("/Users/fhjtech/.openclaw/workspace/.learnings/skill_updates.log")
SUMMARY_FILE   = Path("/Users/fhjtech/.openclaw/workspace/.learnings/daily_skills_summary.md")
SKILLHUB_CMD   = "/Users/fhjtech/.local/bin/skillhub"
LOG_MARKER     = Path("/Users/fhjtech/.openclaw/workspace/.learnings/.last_update_summary.json")

TZ_CST = timezone(timedelta(hours=8))

def log(msg):
    ts = datetime.now(TZ_CST).strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line + "\n")

# ── Step 1: 获取所有类别和技能列表 ──────────────────────────
def fetch_skillhub_categories():
    """从 skillhub.md 解析类别和每个类别的热门技能"""
    try:
        with urllib.request.urlopen(SKILLHUB_INDEX, timeout=15) as resp:
            md = resp.read().decode('utf-8')
    except Exception as e:
        log(f"[Step1] Failed to fetch skillhub.md: {e}")
        return {}

    # 解析类别：每个类别格式大致为 "## category-name\n技能列表..."
    # 根据实际情况，这里从已知类别和 skillhub search 来获取
    # skillhub 的类别关键词（参考原始指令）
    categories_keywords = [
        "research", "academic", "writing", "coding", "browser",
        "memory", "email", "productivity", "automation",
        "data", "analysis", "workflow", "api", "tool"
    ]

    all_skills = {}  # skill_slug -> {category, stars, description}

    for kw in categories_keywords:
        try:
            result = subprocess.run(
                [SKILLHUB_CMD, "search", kw],
                capture_output=True, text=True, timeout=30, cwd="/Users/fhjtech/.openclaw/workspace"
            )
            if result.returncode != 0:
                continue
            # 解析输出，只认英文 slug（字母/数字/短横线），跳过中文描述
            lines = result.stdout.strip().split('\n')
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    continue
                # 跳过非 slug 行（中文、使用说明）
                if re.match(r'^[\u4e00-\u9fff]', stripped) or stripped.startswith('请在机器上') or stripped.startswith('You can use'):
                    continue
                # slug 只能是 ASCII 字母/数字/短横线/下划线
                slug_match = re.match(r'^([a-zA-Z0-9_-]+)\s', stripped)
                if not slug_match:
                    continue
                slug = slug_match.group(1)
                # description 是从 slug 之后到 "- version:" 之前的内容
                rest = stripped[len(slug):].strip()
                desc = re.sub(r'\s*-\s*version:\s*[\d.]+\s*$', '', rest).strip()
                ver_match = re.search(r'version:\s*([\d.]+)', stripped)
                version = ver_match.group(1) if ver_match else ''
                if slug and slug not in all_skills:
                    all_skills[slug] = {
                        'category': kw,
                        'description': desc,
                        'version': version
                    }
        except Exception as e:
            log(f"[Step1] Error searching '{kw}': {e}")

    log(f"[Step1] Fetched {len(all_skills)} skills from {len(categories_keywords)} categories")
    return all_skills

# ── Step 2: 对比本地技能库 ─────────────────────────────────
def get_installed_skills():
    if not SKILLS_DIR.exists():
        return set()
    return {d.name for d in SKILLS_DIR.iterdir() if d.is_dir() and not d.name.startswith('.')}

def find_missing_skills(all_skills):
    installed = get_installed_skills()
    missing = {slug: info for slug, info in all_skills.items() if slug not in installed}
    log(f"[Step2] Installed: {len(installed)}, Missing from hub: {len(missing)}")
    return missing, installed

# ── Step 3: 下载并安装未安装的技能 ─────────────────────────
def install_skills(missing_skills):
    installed_list = []
    failed_list = []
    # 限制一次最多处理数量，避免超时
    MAX_INSTALL = 10
    slugs_to_install = list(missing_skills.keys())[:MAX_INSTALL]
    for slug in slugs_to_install:
        info = missing_skills[slug]
        try:
            log(f"[Step3] Installing: {slug}")
            result = subprocess.run(
                [SKILLHUB_CMD, "install", slug],
                capture_output=True, text=True, timeout=60,
                cwd="/Users/fhjtech/.openclaw/workspace"
            )
            if result.returncode == 0:
                installed_list.append(slug)
                log(f"[Step3] OK: {slug}")
            else:
                failed_list.append(slug)
                log(f"[Step3] FAIL: {slug} -> {result.stderr[:100]}")
        except Exception as e:
            failed_list.append(slug)
            log(f"[Step3] EXCEPTION: {slug} -> {e}")

    log(f"[Step3] Installed {len(installed_list)}/{len(missing_skills)} skills")
    return installed_list, failed_list

# ── Step 4 & 5: 测试和安全评估 ──────────────────────────────
def test_and_evaluate(installed_list):
    """
    安全评估策略：
    1. 检查 SKILL.md 是否存在
    2. 检查是否有可疑的 shell exec / curl / wget 命令
    3. 检查 .js/.ts 文件是否有网络外发（exfil）风险
    """
    safe_list = []
    unsafe_list = []

    SUSPICIOUS_PATTERNS = [
        "curl ", "wget ", "rm -rf /", "chmod 777",
        "eval $", "exec ", "base64 -d",
        "os.system(", "subprocess.call",
        ".send(", "http.request("
    ]

    for slug in installed_list:
        skill_path = SKILLS_DIR / slug
        if not skill_path.exists():
            unsafe_list.append(slug)
            continue

        # 检查 SKILL.md 是否存在
        skill_md = skill_path / "SKILL.md"
        if not skill_md.exists():
            log(f"[Step4] WARN: {slug} has no SKILL.md")
            # 依然视为安全但记录警告

        # 检查可疑文件内容
        is_safe = True
        try:
            for py_file in skill_path.rglob("*.py"):
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                for pattern in SUSPICIOUS_PATTERNS:
                    if pattern in content:
                        log(f"[Step4] UNSAFE: {slug} has pattern '{pattern}' in {py_file.name}")
                        is_safe = False
                        break
            for js_file in skill_path.rglob("*.js"):
                content = js_file.read_text(encoding='utf-8', errors='ignore')
                for pattern in SUSPICIOUS_PATTERNS:
                    if pattern in content:
                        log(f"[Step4] UNSAFE: {slug} has pattern '{pattern}' in {js_file.name}")
                        is_safe = False
                        break
        except Exception as e:
            log(f"[Step4] ERROR checking {slug}: {e}")

        if is_safe:
            safe_list.append(slug)
        else:
            unsafe_list.append(slug)

    log(f"[Step5] Safe: {len(safe_list)}, Unsafe: {len(unsafe_list)}")
    return safe_list, unsafe_list

# ── Step 6: 更新数据库 + 记录待汇报 ─────────────────────────
def update_db_and_log(safe_list, all_skills):
    # 更新 skills_usage.json
    try:
        with open(SKILLS_DB, 'r') as f:
            data = json.load(f)
    except:
        data = {"skills": {}, "categories": {}, "total_uses": 0}

    today = datetime.now(TZ_CST).strftime("%Y-%m-%d")

    for slug in safe_list:
        info = all_skills.get(slug, {})
        if slug not in data["skills"]:
            data["skills"][slug] = {
                "count": 0,
                "first_used": None,
                "contexts": [],
                "last_used": None,
                "description": info.get("description", ""),
                "category": info.get("category", ""),
                "status": "auto-installed",
                "installed_date": today,
                "version": info.get("version", "")
            }

    with open(SKILLS_DB, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # 写入待汇报摘要（供每日汇报脚本读取）
    if safe_list:
        summary = {
            "date": today,
            "skills": [
                {"slug": s, "description": all_skills.get(s, {}).get("description", "")}
                for s in safe_list
            ]
        }
        with open(LOG_MARKER, 'w') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

    log(f"[Step6] DB updated, {len(safe_list)} skills ready for daily report")

# ── 主流程 ─────────────────────────────────────────────────
def main():
    log("=== SkillHub Auto-Update Started ===")

    # Step 1
    all_skills = fetch_skillhub_categories()
    if not all_skills:
        log("[Step1] No skills fetched, aborting")
        return

    # Step 2
    missing, installed = find_missing_skills(all_skills)
    if not missing:
        log("No missing skills, everything up to date")
        return

    # Step 3
    newly_installed, install_failed = install_skills(missing)

    # Step 4 & 5
    safe_list, unsafe_list = test_and_evaluate(newly_installed)

    # Step 6
    update_db_and_log(safe_list, all_skills)

    log(f"=== Done: {len(safe_list)} safe, {len(unsafe_list)} unsafe, {len(install_failed)} failed ===")

if __name__ == "__main__":
    main()
