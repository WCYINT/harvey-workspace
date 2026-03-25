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
async def _fetch_voltagent(semaphore: asyncio.Semaphore, max_retries: int = 1) -> list[dict]:
    """Fetch VoltAgent skills. Reduced to 1 retry since this source consistently times out
    (GitHub raw CDN latency from CN region), wasting ~60s per failed 3-retry run."""
    async with semaphore:
        url = "https://raw.githubusercontent.com/VoltAgent/awesome-openclaw-skills/main/README.md"
        headers = {"User-Agent": "Mozilla/5.0"}

        for attempt in range(max_retries):
            try:
                req = urllib.request.Request(url, headers=headers)
                # 10s timeout sufficient; 20s was causing 60s waste per run (3×20s retries)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    content = resp.read().decode("utf-8", errors="ignore")
                log(f"[VoltAgent] Success on attempt {attempt + 1}")
                return _parse_voltagent_readme(content)
            except Exception as e:
                error_msg = str(e)
                is_timeout = "timed out" in error_msg.lower() or "timeout" in error_msg.lower()

                if attempt < max_retries - 1:
                    wait_time = 2 ** (attempt + 1)
                    error_type = "timeout" if is_timeout else "error"
                    log(f"[VoltAgent] {error_type.capitalize()} on attempt {attempt + 1}: {error_msg[:50]}... Retrying in {wait_time}s")
                    await asyncio.sleep(wait_time)
                else:
                    log(f"[VoltAgent] Failed after {max_retries} attempt(s): {error_msg[:80]}")
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
# ── 统一Slug验证系统 v2.0 ─────────────────────────
# 移除了庞大的INVALID_SLUGS黑名单，改用基于规则的主动验证
# 自动学习：被拒绝的slug会被记录，用于持续改进验证规则

# 仅保留真正模糊的例外情况（这些需要人工判断）
EXCEPTION_CASES = {
    "-",  # 纯连字符
    "llm",  # 可能是合法缩写，但常被误用
}

# 黑名单已移除，改用基于规则的主动验证（见 _is_valid_slug 函数）
# 此处保留空集合作为向后兼容
INVALID_SLUGS = set()

# 被拒绝slug的持久化学习记录
_REJECTED_SLUGS_LOG = Path("/Users/fhjtech/.openclaw/workspace/.learnings/rejected_slugs.json")

def _load_rejected_slugs() -> set[str]:
    """加载历史上被拒绝的slug，用于增强验证"""
    try:
        if _REJECTED_SLUGS_LOG.exists():
            with open(_REJECTED_SLUGS_LOG, "r", encoding="utf-8") as f:
                data = json.load(f)
                return set(data.get("slugs", []))
    except Exception:
        pass
    return set()

def _save_rejected_slug(slug: str) -> None:
    """记录被拒绝的slug，用于持续学习改进"""
    try:
        rejected = _load_rejected_slugs()
        if slug not in rejected:
            rejected.add(slug)
            _REJECTED_SLUGS_LOG.parent.mkdir(parents=True, exist_ok=True)
            with open(_REJECTED_SLUGS_LOG, "w", encoding="utf-8") as f:
                json.dump({
                    "slugs": sorted(list(rejected)),
                    "last_updated": datetime.now(TZ_CST).isoformat(),
                    "count": len(rejected)
                }, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

def _is_valid_slug(slug: str, _learned_rejections: set[str] = None) -> bool:
    """Unified slug validation with proactive pattern matching and automatic learning.
    
    v2.0 Changes:
    - Removed unwieldy INVALID_SLUGS blacklist (89+ entries)
    - Added automatic learning from rejections
    - Consolidated all validation into clear, documented rules
    - Added detailed logging for debugging
    """
    if not slug:
        return False
    
    # Load learned rejections (cached for performance)
    if _learned_rejections is None:
        _learned_rejections = _load_rejected_slugs()
    
    # Rule 1: Known exception cases (truly ambiguous) — silent reject, no logging
    # These are static rules; logging every occurrence creates massive log spam (7000+ entries)
    if slug in EXCEPTION_CASES:
        return False
    
    # Rule 2: Previously learned rejections
    if slug in _learned_rejections:
        log(f"[SlugValidation] Rejected '{slug}': Learned from past failures")
        return False
    
    # Rule 3: Must contain at least one alphabetic character
    if not re.search(r"[a-zA-Z]", slug):
        log(f"[SlugValidation] Rejected '{slug}': No alphabetic characters")
        return False
    
    # Rule 4: Reject pure numeric/hyphen strings
    if re.match(r"^[\d-]+$", slug):
        log(f"[SlugValidation] Rejected '{slug}': Pure numeric/hyphen")
        return False
    
    # Rule 5: Reject common English words (all lowercase, 2-8 chars)
    common_words = {
        "use", "for", "and", "the", "into", "with", "from", "into",
        "add", "new", "get", "set", "run", "all", "any", "are",
        "can", "may", "via", "per", "now", "old", "way", "how",
        "but", "not", "was", "had", "has", "have", "did", "does",
        "will", "would", "could", "should", "shall", "this", "that",
        "these", "those", "they", "them", "their", "there", "then",
        "than", "only", "over", "also", "just", "even", "back",
        "after", "first", "well", "work", "where", "much", "before",
        "right", "think", "too", "take", "still", "being", "here",
        "another", "around", "every", "part", "keep", "call", "came",
        "come", "came", "become", "became", "made", "make", "need",
        "say", "said", "know", "knew", "known", "see", "saw", "seen",
        "seem", "want", "went", "come", "came", "put", "turn", "hand",
        "home", "us", "try", "ask", "end", "why", "let", "point",
        "again", "off", "give", "given", "given", "find", "found",
    }
    if slug.lower() in common_words:
        log(f"[SlugValidation] Rejected '{slug}': Common English word")
        return False
    
    # Rule 6: Reject descriptive phrases with connecting words
    descriptive_patterns = [
        r"comprehensive", r"troubleshooting", r"auto-?detect", r"auto-?invoked",
        r"multi-?platform", r"web-?chat", r"audio-?notifications", r"cli-?tool",
        r"scheduler-?for", r"daemon-?control", r"video-?cog", r"vocal-?chat",
        r"notebook-?lm", r"pr-?commit", r"session-?wrap", r"skill-?gitops",
        r"agent-?builder", r"agent-?team", r"content\d+", r"wrap-?up",
        r"decision", r"gumroad", r"spawn", r"airtable", r"workflowy",
    ]
    for pattern in descriptive_patterns:
        if re.search(pattern, slug, re.IGNORECASE):
            log(f"[SlugValidation] Rejected '{slug}': Descriptive phrase pattern '{pattern}'")
            return False
    
    # Rule 7: Reject common service/brand names (common false positives)
    brand_names = {
        "google", "gmail", "notion", "docker", "github", "slack", "jira",
        "discord", "telegram", "whatsapp", "airtable", "gumroad", "stripe",
        "paypal", "amazon", "aws", "azure", "gcp", "heroku", "vercel",
        "netlify", "cloudflare", "datadog", "splunk", "elasticsearch",
        "mongodb", "postgres", "mysql", "redis", "kafka", "rabbitmq",
        "clawhub", "skillhub", "voltagent", "openclaw", "skills.sh",
        "github", "gitlab", "bitbucket", "jira", "confluence", "trello",
        "asana", "monday", "notion", "obsidian", "evernote", "onenote",
        "dropbox", "googledrive", "onedrive", "box", "icloud",
        "figma", "sketch", "adobe", "canva", "photoshop", "illustrator",
        "vscode", "intellij", "pycharm", "webstorm", "sublime", "atom",
        "vim", "emacs", "nano", "cursor", "windsurf", "trae",
        "macos", "windows", "linux", "ubuntu", "debian", "centos", "redhat",
        "android", "ios", "iphone", "ipad", "watch", "tv",
    }
    if slug.lower() in brand_names:
        log(f"[SlugValidation] Rejected '{slug}': Brand/service name")
        return False
    
    # Rule 8: Additional structural validation
    # Reject slugs that are just numbers with common suffixes
    if re.match(r"^\d+(st|nd|rd|th|px|em|rem|vh|vw|%)$", slug, re.IGNORECASE):
        log(f"[SlugValidation] Rejected '{slug}': Numeric with suffix pattern")
        return False
    
    # Rule 9: Reject obvious file extensions or MIME types
    file_extensions = {
        "jpg", "jpeg", "png", "gif", "svg", "webp", "bmp", "tiff",
        "mp3", "mp4", "wav", "avi", "mov", "mkv", "flv", "wmv",
        "pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx",
        "txt", "csv", "json", "xml", "yaml", "yml", "toml", "ini",
        "html", "htm", "css", "js", "jsx", "ts", "tsx", "php", "py", "rb",
        "go", "rs", "java", "kt", "swift", "scala", "clj", "erl",
        "zip", "tar", "gz", "bz2", "7z", "rar", "xz",
        "sql", "db", "sqlite", "mdb", "accdb",
    }
    if slug.lower() in file_extensions or re.match(r"^[a-z]+\d+$", slug, re.IGNORECASE):
        if slug.lower() in file_extensions:
            log(f"[SlugValidation] Rejected '{slug}': File extension pattern")
            return False
    
    # All validation passed - slug looks valid
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
            return (slug, ok, status)
        except asyncio.TimeoutError:
            return (slug, False, "Timeout")
        except Exception as e:
            log(f"[Step3] EXCEPTION {slug}: {e}")
            return (slug, False, str(e))

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
    fail_list = [(slug, reason) for slug, ok, reason in results if not ok]
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
def _gen_usage_suggestion(slug: str, description: str) -> str:
    """根据技能名和描述自动生成用途建议"""
    desc_lower = (description + " " + slug).lower()

    # 关键词映射到用途场景
    scenarios = []
    if any(k in desc_lower for k in ["github", "code", "coding", "git", "debug", "repo"]):
        scenarios.append("代码开发与Git管理")
    if any(k in desc_lower for k in ["research", "search", "web", "fetch", "scrape"]):
        scenarios.append("网络研究与信息检索")
    if any(k in desc_lower for k in ["email", "mail", "smtp", "inbox"]):
        scenarios.append("邮件自动处理与回复")
    if any(k in desc_lower for k in ["paper", "academic", "thesis", "writing", "write"]):
        scenarios.append("学术论文写作辅助")
    if any(k in desc_lower for k in ["debug", "error", "log", "monitor", "health"]):
        scenarios.append("系统监控与故障排查")
    if any(k in desc_lower for k in ["file", "document", "doc", "pdf", "read"]):
        scenarios.append("文档处理与知识管理")
    if any(k in desc_lower for k in ["browser", "web", "click", "screenshot"]):
        scenarios.append("浏览器自动化操作")
    if any(k in desc_lower for k in ["image", "video", "media", "visual"]):
        scenarios.append("多媒体内容分析与处理")
    if any(k in desc_lower for k in ["data", "analysis", "analytics", "sql", "database"]):
        scenarios.append("数据分析与数据库操作")
    if any(k in desc_lower for k in ["schedule", "cron", "time", "remind", "alarm"]):
        scenarios.append("定时任务与日程管理")
    if any(k in desc_lower for k in ["test", "pytest", "unit", "coverage"]):
        scenarios.append("自动化测试与质量保障")
    if any(k in desc_lower for k in ["deploy", "docker", "k8s", "cloud", "server"]):
        scenarios.append("部署与云服务管理")
    if any(k in desc_lower for k in ["security", "audit", "scan", "firewall"]):
        scenarios.append("安全审计与风险检测")
    if any(k in desc_lower for k in ["feishu", "slack", "discord", "telegram", "chat"]):
        scenarios.append("企业通讯与群聊管理")

    # 默认场景
    if not scenarios:
        scenarios = ["通用辅助（待人工分类）"]

    return " | ".join(scenarios[:2])  # 最多2个场景


def _test_skill(slug: str) -> tuple[str, str]:
    """对已安装技能进行快速测试，返回 (测试结果, 详情)"""
    sp = SKILLS_DIR / slug
    skill_md = sp / "SKILL.md"
    if not skill_md.exists():
        return "❌", "缺少 SKILL.md"
    try:
        content = skill_md.read_text(encoding="utf-8", errors="ignore")
        if len(content) < 50:
            return "❌", f"SKILL.md 内容过短({len(content)}字符)"
        if len(content) < 200:
            return "⚠️", f"内容偏少({len(content)}字符)，建议补充"
        # 检查关键字段
        has_desc = "description" in content.lower() or "功能" in content
        has_usage = "usage" in content.lower() or "使用" in content
        if has_desc and has_usage:
            return "✅", "结构完整"
        elif has_desc:
            return "✅", "描述完整（待补充使用说明）"
        else:
            return "✅", "基础完整"
    except Exception as e:
        return "❌", str(e)


def send_install_report(integrated, fail_list, unsafe, all_skills):
    EMAIL_FROM, EMAIL_TO = "wcyint@163.com", "wcyint@163.com"
    SMTP_HOST, SMTP_PORT = "smtp.163.com", 465
    EMAIL_PASSWORD = "PWvrfWXa6PXWiQLn"

    now = datetime.now(TZ_CST)
    subject = f"📦 技能自动更新 | {now.strftime('%m-%d %H:%M')} | +{len(integrated)}个 ⭐用途建议已附"

    rows = ""
    for s in integrated:
        desc = all_skills.get(s, {}).get("description", "")[:80]
        source = all_skills.get(s, {}).get("source", "")
        test_result, test_detail = _test_skill(s)
        suggestion = _gen_usage_suggestion(s, desc)

        rows += f"""<tr>
            <td><code>{s}</code><br><span style='font-size:11px;color:#888'>{test_detail}</span></td>
            <td>{test_result}</td>
            <td>{source}</td>
            <td style='max-width:200px;font-size:12px'>{desc}</td>
            <td style='font-size:12px;color:#0066cc'>{suggestion}</td>
        </tr>"""

    # 失败/skipped技能的详情
    fail_rows = ""
    for slug, reason in fail_list:
        fail_rows += f"<tr><td><code>{slug}</code></td><td>❌安装失败</td><td>{reason[:60]}</td></tr>"
    for slug, reason in unsafe:
        fail_rows += f"<tr><td><code>{slug}</code></td><td>🚫安全拦截</td><td>{reason[:60]}</td></tr>"

    body = f"""
    <h2>📦 技能自动更新报告</h2>
    <p><b>时间：</b>{now.strftime('%Y-%m-%d %H:%M')} (北京时间)</p>
    <p><b>新安装：</b>{len(integrated)} 个 &nbsp;
       <b>安装失败：</b>{len(fail_list)} 个 &nbsp;
       <b>安全拦截：</b>{len(unsafe)} 个</p>

    <h3>✅ 新技能详情（含测试结果 + 用途建议）</h3>
    <table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;width:100%;font-size:13px">
        <tr style="background:#e8f5e9">
            <th>技能名</th><th>测试</th><th>来源</th><th>描述</th><th>🎯 用途建议</th>
        </tr>
        {rows or '<tr><td colspan=5">无新技能</td></tr>'}
    </table>

    {"<h3>⚠️ 失败/拦截记录</h3><table border='1' cellpadding='4' cellspacing='0' style='border-collapse:collapse;width:60%'><tr style=background:#ffebee><th>技能</th><th>状态</th><th>原因</th></tr>" + fail_rows + "</table>" if fail_rows else ""}

    <hr>
    <p style="color:#555;font-size:12px">
    📋 <b>测试说明：</b>✅=通过 | ⚠️=内容偏少 | ❌=失败<br>
    🎯 <b>用途建议：</b>基于技能名称和描述的关键词自动推断，仅供参考，请根据实际情况选用
    </p>
    """

    next_steps = f"""
    <h3>📋 下一步计划</h3>
    <ul>
        <li><b>短期（本周）：</b>根据用途建议，人工筛选出与 MBA 论文修改最相关的技能重点使用</li>
        <li><b>中期（本月）：</b>跟踪本次安装技能的的实际调用效果，形成技能使用反馈闭环</li>
        <li><b>长期（本季度）：</b>基于本次测试结果，优化用途建议的关键词映射表，提升推断准确率</li>
    </ul>
    <p style="color:#888;font-size:12px">由 Harvey 自动生成 | 四源技能发现系统 (SkillHub+ClawHub+VoltAgent+Skills.sh)</p>
    """

    body += next_steps

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
    send_install_report(integrated, install_failed, unsafe, all_skills)
    log(f"=== 完成: 集成{len(integrated)} | 安全{len(safe)} | 安装{len(newly_installed)} ===")

if __name__ == "__main__":
    main()
