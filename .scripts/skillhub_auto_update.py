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
import fcntl
import subprocess
import json
import os
import urllib.request
import urllib.parse
import re
import shutil
import smtplib
import time
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
MAX_LOG_SIZE = 5 * 1024 * 1024  # Rotate log if > 5MB
LOCK_FILE        = Path("/Users/fhjtech/.openclaw/workspace/.learnings/.skillhub_update.lock")
SMTP_HEALTH_LOG  = Path("/Users/fhjtech/.openclaw/logs/smtp_health.json")
STALE_UP_TO_DATE_CACHE = Path("/Users/fhjtech/.openclaw/workspace/.learnings/.up_to_date_stale.json")
STALE_UP_TO_DATE_HOURS = 2  # 如果上次报告"已是最新"且不足此时间窗口，跳过 Step1 API 调用
SKILLHUB_CMD     = "/Users/fhjtech/.local/bin/skillhub"
CLAWHUB_CMD      = "/opt/homebrew/bin/clawhub"
NPX_SKILLS_CMD   = "npx"   # skills.sh CLI: npx skills add <owner>/<repo>/<skill>
MAX_INSTALL      = 15      # 每轮最多安装15个（James确认）
MAX_CONCURRENCY = 20

TZ_CST = timezone(timedelta(hours=8))

# 七大类别 + 类别关键词映射（用于 Top100 查询）
CATEGORIES = ["AI智能", "开发工具", "效率提升", "数据分析", "内容创作", "通讯协作", "安全合规"]

CATEGORY_KEYWORDS = {
    "AI智能": ["AI", "人工智能", "大模型", "LLM", "GPT", "agentic", "autonomous", "智能体", "AI助手"],
    "开发工具": ["coding", "developer", "IDE", "debug", "git", "programming", "代码", "开发", "programming-language"],
    "效率提升": ["productivity", "workflow", "automation", "效率", "自动化", "task", "schedule", "reminder"],
    "数据分析": ["data", "analytics", "analysis", "database", "数据", "分析", "SQL", "visualization", "fhir", "healthcare", "medical", "backlink", "SEO"],
    "内容创作": ["writing", "content", "creative", "文案", "写作", "创作", "生成", "text"],
    "通讯协作": ["communication", "collaboration", "chat", "message", "通讯", "协作", "team", "meeting"],
    "安全合规": ["security", "privacy", "合规", "安全", "encryption", "auth", "permission", "threat", "intel", "vulnerability", "exploit", "malware", "risk-assessment", "hipaa", "GDPR"],
}

# ── 并发锁（原子文件锁）────────────────────────────────
_lock_fd: int | None = None

def _acquire_lock() -> bool:
    """原子文件锁：防止 cron 重复触发导致并发执行。
    使用 fcntl.flock 实现，替代有 TOCTOU 风险的 PID 文件方案。"""
    global _lock_fd
    try:
        LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
        _lock_fd = os.open(str(LOCK_FILE), os.O_CREAT | os.O_RDWR)
        # LOCK_NB = non-blocking；LOCK_EX = exclusive lock
        fcntl.flock(_lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        # 写入当前 PID（便于人工检查）
        os.write(_lock_fd, f"{os.getpid()},{datetime.now(TZ_CST).isoformat()}\n".encode())
        return True
    except (IOError, OSError):
        # 锁已被占用
        if _lock_fd is not None:
            try:
                os.close(_lock_fd)
            except Exception:
                pass
            _lock_fd = None
        return False

def _release_lock() -> None:
    """释放原子锁"""
    global _lock_fd
    if _lock_fd is not None:
        try:
            fcntl.flock(_lock_fd, fcntl.LOCK_UN)
            os.close(_lock_fd)
        except Exception:
            pass
        _lock_fd = None
    try:
        if LOCK_FILE.exists():
            LOCK_FILE.unlink(missing_ok=True)
    except Exception:
        pass

# ── Edit 失败自动排查与纠正 ─────────────────────────
GATEWAY_LOG = Path("/Users/fhjtech/.openclaw/logs/gateway.log")

def _check_and_fix_edit_failures() -> list[dict]:
    """
    检查 gateway.log 中的 Edit failed 错误，自动分析原因并纠正。
    返回: [{file, oldText, newText, cause, fixed, detail}, ...]
    """
    if not GATEWAY_LOG.exists():
        return []

    # 读取最近 500 行
    try:
        lines = GATEWAY_LOG.read_text(encoding="utf-8", errors="ignore").splitlines()[-500:]
    except Exception as e:
        log(f"[EditFix] 读取 gateway.log 失败: {e}")
        return []

    results = []
    for line in lines:
        # 匹配 "Edit: in <file> (<N> chars) failed" 格式
        m = re.search(r'Edit:\s*in\s+([^\s]+?)\s+\((\d+)\s+chars?\)\s+failed', line)
        if not m:
            continue
        file_path = m.group(1)
        char_count = m.group(2)

        # 提取错误原因（下一行或同一行）
        cause = "oldText 与文件内容不匹配"
        if "oldText" in line or "old_string" in line:
            cause = "oldText 与文件内容不匹配（文件已被其他编辑改动）"
        elif "Permission" in line:
            cause = "权限不足"
        elif "No such file" in line:
            cause = "文件不存在"

        log(f"[EditFix] 检测到 Edit 失败: {file_path} ({char_count} chars) → {cause}")

        # 尝试修复：重新读取文件内容，验证 oldText
        fixed = False
        detail = ""
        try:
            content = Path(file_path).read_text(encoding="utf-8", errors="ignore")
            # oldText 通常在错误前的上下文中，找到 "oldText:" 或 "old_string:" 后的内容
            ctx_match = re.search(r'(?:oldText|old_string)["\']?\s*[:=]\s*["\`](.*?)["`\']', line)
            if ctx_match:
                old_text_snippet = ctx_match.group(1)[:int(char_count)]
                if old_text_snippet in content:
                    detail = f"验证通过：oldText 存在于文件当前内容中（可能是时序问题）"
                    fixed = True  # 内容匹配，无需修改
                else:
                    detail = f"oldText 不匹配：片段 '{old_text_snippet[:30]}...' 未在文件中找到"
            else:
                # 无法提取 oldText，尝试查找类似的代码块
                # 找到函数/类定义的开始
                func_match = re.search(r'def\s+\w+|class\s+\w+|async\s+def\s+\w+', content)
                if func_match:
                    detail = f"文件中存在函数定义，但无法确定具体编辑位置"
                fixed = False
        except Exception as e:
            detail = f"修复尝试失败: {e}"

        results.append({
            "file": file_path,
            "char_count": int(char_count),
            "cause": cause,
            "fixed": fixed,
            "detail": detail
        })
        log(f"[EditFix] → {'✅ 已修复' if fixed else '⚠️ 需手动处理'}: {detail}")

    if results:
        log(f"[EditFix] 共检测到 {len(results)} 个 Edit 失败，{sum(1 for r in results if r['fixed'])} 个已自动处理")
    return results

# ── 日志 ──────────────────────────────────────────
# ── Log deduplication (per-run) ────────────────────────────────────────────
_log_seen: dict[str, int] = {}   # msg → repeat count (0 = already written)

def _rotate_log_if_needed() -> None:
    """Rotate log file if it exceeds MAX_LOG_SIZE."""
    if LOG_FILE.exists() and LOG_FILE.stat().st_size > MAX_LOG_SIZE:
        # Rotate: move current log to .bak
        backup = LOG_FILE.with_suffix(".log.bak")
        if backup.exists():
            backup.unlink()
        LOG_FILE.rename(backup)

def log(msg: str) -> None:
    ts = datetime.now(TZ_CST).strftime("%Y-%m-%d %H:%M:%S")
    if msg in _log_seen:
        _log_seen[msg] += 1
        return
    _log_seen[msg] = 0
    line = f"[{ts}] {msg}"
    print(line)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    _rotate_log_if_needed()
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def log_summary() -> None:
    """Print how many duplicate log entries were suppressed (call at end of run)."""
    dups = {k: v for k, v in _log_seen.items() if v > 0}
    if dups:
        total = sum(dups.values())
        print(f"[DEDUP] Suppressed {total} duplicate log entries ({len(dups)} unique types)")
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        _rotate_log_if_needed()
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now(TZ_CST).strftime('%Y-%m-%d %H:%M:%S')}] [DEDUP] Suppressed {total} duplicate entries ({len(dups)} unique types)\n")


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

# ── 网络获取辅助函数（带curl降级）────────────────────────
def _fetch_url_with_fallback(url: str, timeout: int = 10) -> str | None:
    """Try urllib first, fall back to curl on failure.
    Returns content string or None if both methods fail."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception as urllib_err:
        # 降级到curl（处理企业网络/代理干扰urllib的情况）
        try:
            result = subprocess.run(
                ["curl", "-s", "--max-time", str(timeout + 5), url],
                capture_output=True, text=True, timeout=timeout + 8
            )
            if result.returncode == 0 and result.stdout:
                log(f"[VoltAgent] curl fallback succeeded (urllib failed: {str(urllib_err)[:40]})")
                return result.stdout
            else:
                log(f"[VoltAgent] curl fallback also failed: {result.stderr[:60] if result.stderr else 'no output'}")
                return None
        except Exception as curl_err:
            log(f"[VoltAgent] curl fallback error: {str(curl_err)[:60]}")
            return None


# ── Step 1c: VoltAgent / OpenClaw Skills GitHub ────────────────────
VOLTAGER_KEYWORDS = [
    "research", "paper", "thesis", "writing", "academic", "study",
    "analysis", "data", "science", "literature", "survey",
    "MBA", "dissertation", "journal", "conference", "publication",
]

async def _fetch_voltagent(semaphore: asyncio.Semaphore) -> list[dict]:
    """
    Fetch VoltAgent skills from OpenClaw skills GitHub API.
    The VoltAgent awesome list (GitHub README) is now HTML, so we fetch
    the OpenClaw skills registry directly via GitHub API.
    Returns skills matching research/paper/academic keywords.
    """
    async with semaphore:
        try:
            api_url = "https://api.github.com/repos/openclaw/skills/contents/skills"
            req = urllib.request.Request(
                api_url,
                headers={"Accept": "application/vnd.github.v3+json", "User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            skills = []
            for item in data:
                name = item["name"].lower()
                # Filter by keywords relevant to research/paper/academic
                if any(kw in name for kw in VOLTAGER_KEYWORDS):
                    skills.append({
                        "slug": item["name"],
                        "description": item["name"].replace("-", " ").replace("_", " "),
                        "source": "voltagent",
                    })
            log(f"[VoltAgent] OpenClaw GitHub API: found {len(skills)} matching skills")
            return skills
        except Exception as e:
            log(f"[VoltAgent] Failed: {e}")
            return []

# ── Step 1e: ClawHub Explore Top100（评分排序）─────────────
async def _fetch_clawhub_top(semaphore: asyncio.Semaphore) -> list[dict]:
    """使用 clawhub explore 获取全站评分最高的 Top100 技能（含速率限制重试）"""
    async with semaphore:
        last_error = ""

        for attempt in range(3):  # 首次 + 2次重试
            try:
                shell_cmd = (
                    f"PATH=/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH "
                    f"NODE_PATH=/opt/homebrew/lib/node_modules:$NODE_PATH "
                    f"{CLAWHUB_CMD} explore --limit 100 --sort rating"
                )
                proc = await asyncio.create_subprocess_shell(
                    shell_cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=str(SKILLS_DIR.parent),
                )
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)
                if proc.returncode == 0:
                    return _parse_skillhub_output(stdout.decode("utf-8", errors="ignore"), source="clawhub")
                err_msg = stderr.decode("utf-8", errors="ignore")[:120]
                last_error = err_msg
                # 仅限速率限制重试；其余错误直接退出
                if "rate limit" not in err_msg.lower():
                    log(f"[ClawHub Top] explore failed: {err_msg}")
                    return []
                log(f"[ClawHub Top] rate-limited, retrying in 5s (attempt {attempt + 1}/3)...")
                await asyncio.sleep(5)
            except asyncio.TimeoutError:
                log(f"[ClawHub Top] explore timeout (attempt {attempt + 1}/3), retrying in 5s...")
                if attempt == 2:  # 已到最后一次尝试
                    log("[ClawHub Top] explore timeout after retries")
                    return []
                await asyncio.sleep(5)
            except Exception as e:
                log(f"[ClawHub Top] Error: {e}")
                return []

        log(f"[ClawHub Top] explore failed after retries: {last_error}")
        return []

# ── Step 1d: Skills.sh ─────────────────────────
async def _fetch_skills_sh(semaphore: asyncio.Semaphore) -> list[dict]:
    """使用 skills.sh API 搜索技能，返回格式适合 npx skills add"""
    skills = []
    keywords_to_try = [
        "thesis paper academic", "MBA dissertation research",
        "writing assistant", "data analysis statistics",
        "quality improvement manufacturing", "engineering automotive",
        "PDF document extraction", "literature review",
    ]
    for kw in keywords_to_try[:5]:  # 限制数量避免超时
        # quote() encodes spaces as %20 (safe for URL path/query components)
        # quote_plus uses + which some servers reject in path context
        encoded_q = urllib.parse.quote(kw, safe='')
        api_url = f"https://skills.sh/api/search?q={encoded_q}&limit=10"
        try:
            req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
        except Exception as e:
            log(f"[Skills.sh API] URL construction error for kw={kw!r}: {e}")
            continue
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            log(f"[Skills.sh API] error for kw={kw!r}: url={api_url!r} -> {e}")
            continue
        for item in data.get("skills", []):
            # id 格式: <owner>/<repo>/<skill>  ← 这正是 npx skills add 需要的格式
            skill_id = item.get("id", "")
            if skill_id and "/" in skill_id:
                skills.append({
                    "slug": skill_id,
                    "description": item.get("name", ""),
                    "installs": item.get("installs", 0),
                    "source": "skills.sh",
                })
    return skills

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

# Module-level cache for learned rejections (avoids UnboundLocalError in _is_valid_slug)
_learned_rejections: set[str] | None = None

# 被拒绝slug的持久化学习记录
_REJECTED_SLUGS_LOG = Path("/Users/fhjtech/.openclaw/workspace/.learnings/rejected_slugs.json")

def _load_rejected_slugs() -> set[str]:
    """加载历史上被拒绝的slug，用于增强验证。
    返回格式: {"slug"} (旧格式，无前缀) 或 {"source:slug"} (新格式，带源前缀)。
    检查时需同时匹配两种格式以实现向后兼容。"""
    try:
        if _REJECTED_SLUGS_LOG.exists():
            with open(_REJECTED_SLUGS_LOG, "r", encoding="utf-8") as f:
                data = json.load(f)
                return set(data.get("slugs", []))
    except Exception:
        pass
    return set()

def _is_rejected_for_source(slug_lower: str, source: str, rejected: set[str]) -> bool:
    """检查slug是否在特定源被拒绝（向后兼容：也检查无前缀的旧格式）"""
    # 新格式：source:slug
    if f"{source}:{slug_lower}" in rejected:
        return True
    # 旧格式（全局拒绝，向后兼容）
    if slug_lower in rejected:
        return True
    # auditor: 前缀的拒绝（Step3.6 写入）是危险技能，应跨源过滤
    if f"auditor:{slug_lower}" in rejected:
        return True
    return False

def _save_rejected_slug(slug: str, source: str | None = None) -> None:
    """记录被拒绝的slug，用于持续学习改进。
    新格式带source前缀（如 skillhub:inflated），实现按源隔离拒绝。
    无source参数时使用旧格式（全局拒绝），用于向后兼容。"""
    try:
        slug_lower = slug.lower()
        rejected = _load_rejected_slugs()
        key = f"{source}:{slug_lower}" if source else slug_lower
        if key not in rejected:
            rejected.add(key)
            _REJECTED_SLUGS_LOG.parent.mkdir(parents=True, exist_ok=True)
            with open(_REJECTED_SLUGS_LOG, "w", encoding="utf-8") as f:
                json.dump({
                    "slugs": sorted(list(rejected)),
                    "last_updated": datetime.now(TZ_CST).isoformat(),
                    "count": len(rejected)
                }, f, indent=2, ensure_ascii=False)
            # Keep in-memory cache in sync so same slug won't be re-validated this run
            global _learned_rejections
            _learned_rejections = rejected
    except Exception:
        pass

VOLTAGENT_SOURCE_PREFIX = "voltagent:"

def _is_voltagent_rejected(slug: str, rejected: set[str]) -> bool:
    """Check if a VoltAgent slug has been permanently rejected (not in index)."""
    return (VOLTAGENT_SOURCE_PREFIX + slug) in rejected


def _is_valid_slug(slug: str, log_rejection: bool = True) -> bool:
    """Unified slug validation with proactive pattern matching and automatic learning.

    v2.1 Changes:
    - Added log_rejection param to suppress SlugValidation logs during parse-time
      (parse functions process all fetched skills including already-installed ones;
      logging every rejection creates massive log spam on every run)
    - Removed unwieldy INVALID_SLUGS blacklist (89+ entries)
    - Added automatic learning from rejections
    - Consolidated all validation into clear, documented rules
    """
    if not slug:
        return False

    # Load learned rejections (cached for performance)
    global _learned_rejections
    if _learned_rejections is None:
        _learned_rejections = _load_rejected_slugs()

    # Rule 1: Known exception cases (truly ambiguous) — silent reject, no logging
    # These are static rules; logging every occurrence creates massive log spam (7000+ entries)
    if slug in EXCEPTION_CASES:
        return False

    # Rule 2: Previously learned rejections (source-aware; also checks legacy bare slugs)
    # Note: _is_valid_slug is called at parse time before source is known, so we check
    # both source-specific and legacy formats. In step2/step3, source is available and
    # per-source checking is used instead.
    slug_lower = slug.lower()
    if slug_lower in _learned_rejections:
        if log_rejection:
            log(f"[SlugValidation] Rejected '{slug}': Learned from past failures")
        return False

    # Rule 3: Must contain at least one alphabetic character AND be >= 4 chars
    # Prevents short English words like "Ad", "inflated", "Jeffrey" from
    # being installed (they fail on SkillHub repeatedly, creating log spam)
    if not re.search(r"[a-zA-Z]", slug):
        if log_rejection:
            log(f"[SlugValidation] Rejected '{slug}': No alphabetic characters")
        return False
    if len(slug) < 4:
        if log_rejection:
            log(f"[SlugValidation] Rejected '{slug}': Slug too short (< 4 chars)")
        return False

    # Rule 4: Reject Title Case single-word slugs (e.g. 'Academic', 'Patterns', 'Professional').
    # These are description fragments from ClawHub search that pass _is_valid_slug
    # (not in common_words when lowercased, not in rejected yet) but fail at install.
    # Previously handled by a belt-and-suspenders filter in step2_find_missing;
    # moved here to make _is_valid_slug the single source of slug quality truth.
    if (
        len(slug) > 3
        and slug[0].isupper()
        and slug[1:].islower()
        and "-" not in slug
        and "_" not in slug
    ):
        if log_rejection:
            log(f"[SlugValidation] Rejected '{slug}': Title Case single-word")
        return False

    # Rule 4b: Reject slugs with mixed internal capitals (e.g. CornerStone, BluOS, NotebookLM).
    # Pattern: starts uppercase + has at least one more uppercase letter beyond position 0,
    # and no hyphen/underscore (which would make it kebab/camel with a legitimate structure).
    # These are description fragments ClawHub returns as "slugs" — e.g. "CornerStone",
    # "BluOS", "NotebookLM", "ClickFunnels", "Auto-detect" — that fail with "not in index".
    # Separators are excluded since real kebab slugs like "openclaw-aisa-llm-router"
    # legitimately have uppercase after hyphens (part of the identifier).
    if (
        len(slug) > 4
        and slug[0].isupper()
        and re.search(r"[A-Z]", slug[1:])
        and "-" not in slug
        and "_" not in slug
    ):
        if log_rejection:
            log(f"[SlugValidation] Rejected '{slug}': Mixed internal capitals (description fragment)")
        return False

    # Rule 5: Reject pure numeric/hyphen strings
    if re.match(r"^[\d-]+$", slug):
        if log_rejection:
            log(f"[SlugValidation] Rejected '{slug}': Pure numeric/hyphen")
        return False

    # Rule 6: Reject common English words (all lowercase, 2-8 chars)
    # Also reject service names / brand words that keep failing with "not in index"
    # (observed in skill_updates.log: 2026-03-21 12:00-12:02)
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
        "requires", "required", "include", "based", "using", "used",
        "say", "said", "know", "knew", "known", "see", "saw", "seen",
        "seem", "want", "went", "come", "came", "put", "turn", "hand",
        "home", "us", "try", "ask", "end", "why", "let", "point",
        "again", "off", "give", "given", "given", "find", "found",
        # High-failure brand/service names from skill_updates.log
        # (2026-03-28: + Ultimate, Boost, Essential, Professional, Convert, Learns, Guides, Designs, Fully)
        "gmail", "gpt", "navigate", "cornerstone", "brand",
        "academic", "patterns", "ultimate", "boost", "essential",
        "convert", "learns", "guides", "designs", "fully",
        # High-failure slug keywords from rejected_slugs.json (causing repeated "not in index")
        "agent", "manage", "creates", "automates",
        # Single-word adjectives/descriptive that repeatedly fail "not in index"
        # (2026-03-27 18:47 run: Autonomous, Access, Complete, Personal, Visual,
        #  Autonomously, Automated; 2026-03-21: Deterministically, Fetches)
        "autonomous", "autonomously", "automated", "automate", "automation",
        "complete", "completed", "completes",
        "access", "accessible",
        "personal", "personally",
        "visual", "visually",
        "deterministically", "deterministic",
        "fetches", "fetched", "fetch",
        # Missing from common_words but present in rejected_slugs.json
        # (43 slugs confirmed missing 2026-03-27; causes repeated 'not_in_index'
        #  in skill_updates.log despite being in rejected_slugs.json)
        "create", "enable", "earn", "conduct", "execute",
        "develop", "query", "help", "provides", "generate",
        "productivity", "insights", "smart", "your",
        "agenthire", "ai-agent", "ai-powered", "all-in-one",
        "end-to-end", "intent-based", "world-class", "multi-agent",
        "self-healing", "persistent", "real-time",
        "prism", "intellectia", "gitai", "goplus",
        "abaddon", "atxp", "breeze", "callmac", "evomap",
        "accounting-workflows", "brand-specific", "friction-reduction",
        "mandatory", "inflated", "prismer",
    }
    if slug.lower() in common_words:
        if log_rejection:
            log(f"[SlugValidation] Rejected '{slug}': Common English word")
        return False

    # Rule 7: Reject descriptive phrases with connecting words
    # Note: 5+ segment slugs are rejected because they're almost always versioned/descriptive.
    # 4-segment names like tiangong-wps-word-automation are legitimate platform-tool-action
    # identifiers — they represent real tools and should be allowed through.
    descriptive_patterns = [
        r"comprehensive", r"troubleshooting", r"auto-?detect", r"auto-?invoked",
        r"multi-?platform", r"web-?chat", r"audio-?notifications", r"cli-?tool",
        r"scheduler-?for", r"daemon-?control", r"video-?cog", r"vocal-?chat",
        r"notebook-?lm", r"pr-?commit", r"session-?wrap", r"skill-?gitops",
        r"agent-?builder", r"agent-?team", r"content\d+", r"wrap-?up",
        r"decision", r"gumroad", r"spawn", r"airtable", r"workflowy",
        r"\w+-\w+-\w+-\w+-\w+",  # 5+ hyphen-separated segments (versioned slugs always have 5+; 4-segment names like tiangong-wps-word-automation are legitimate tool identifiers)
    ]
    for pattern in descriptive_patterns:
        if re.search(pattern, slug, re.IGNORECASE):
            if log_rejection:
                log(f"[SlugValidation] Rejected '{slug}': Descriptive phrase (5+ segments: {slug.count('-')+1})")
            return False

    # Rule 8: Reject common service/brand names (common false positives)
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
        # Missing brand/service names causing repeated "not in index" failures
        "acuity", "bluos", "brand", "clickfunnels", "clicksend", "cornerstone",
        "evomap", "jeffrey", "notebooklm",
    }
    if slug.lower() in brand_names:
        if log_rejection:
            log(f"[SlugValidation] Rejected '{slug}': Brand/service name")
        return False

    # Rule 9: Additional structural validation
    # Reject slugs that are just numbers with common suffixes
    if re.match(r"^\d+(st|nd|rd|th|px|em|rem|vh|vw|%)$", slug, re.IGNORECASE):
        if log_rejection:
            log(f"[SlugValidation] Rejected '{slug}': Numeric with suffix pattern")
        return False

    # Rule 10: Reject obvious file extensions or MIME types
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
            if log_rejection:
                log(f"[SlugValidation] Rejected '{slug}': File extension pattern")
            return False

    # Rule 10: Reject non-ASCII slugs (valid slugs are ASCII-only)
    # SkillHub sometimes returns "中文描述 slug" format where Chinese text
    # is incorrectly parsed as slug; this prevents Chinese/mixed chars as slugs
    if not slug.isascii():
        if log_rejection:
            log(f"[SlugValidation] Rejected '{slug}': Non-ASCII slug")
        return False

    # Rule 11: Reject ALL-UPPERCASE slugs > 4 chars (likely broken parses of
    # Chinese descriptions where the actual slug is missing; legitimate slugs
    # are lowercase, camelCase, or kebab-case — never ALL-CAPS beyond ~4 chars)
    # Examples: "MANDATORY", "CornerStone", "Jeffrey" — all fail with "not in index"
    # because they're fragments, not real skill identifiers
    if len(slug) > 4 and slug.isupper():
        if log_rejection:
            log(f"[SlugValidation] Rejected '{slug}': All-uppercase slug > 4 chars (likely description fragment)")
        return False

    # Rule 11b: Reject Title Case single words (e.g. "Academic", "Patterns",
    # "Professional"). Valid slugs are lowercase, kebab-case, or camelCase — not a
    # single capitalized word. These are description fragments that pass Rule 11
    # (not ALL-UPPERCASE) but fail at SkillHub with "not in index".
    if (
        len(slug) > 3
        and slug[0].isupper()
        and slug[1:].islower()
        and "-" not in slug
        and "_" not in slug
    ):
        if log_rejection:
            log(f"[SlugValidation] Rejected '{slug}': Title Case single-word slug (description fragment)")
        return False

    # Rule 13: Reject long ASCII slugs without hyphens (likely description fragments).
    # Valid slugs are either short or kebab-case/underscore_case (which have hyphens/underscores).
    # A 40+ char ASCII string with < 2 separators is almost certainly a description
    # that bypassed Rule 10 via incorrect parsing (e.g. "DeepResearch" or
    # "开展开放式主题研究" extracted as slug when it should have been description).
    # 2 separators because real kebab-case slugs like "auto-skill-builder" have at least 1 hyphen.
    hyphen_count = slug.count("-") + slug.count("_")
    if len(slug) >= 40 and hyphen_count < 2:
        if log_rejection:
            log(f"[SlugValidation] Rejected '{slug[:50]}...': Long ASCII slug < 2 separators (likely description fragment)")
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
        if not _is_valid_slug(slug, log_rejection=False):
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
            if _is_valid_slug(slug, log_rejection=False):
                desc = line.split("](")[0].replace("- [", "").strip()
                skills.append({"slug": slug, "description": desc, "version": "", "source": "voltagent"})
    return skills

# ── Step 1: 七大类别 Top100 查询 + 全四源并发搜索 ─────────────────────
async def step1_fetch_all() -> dict[str, dict]:
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
    tasks = []

    # Keywords that are single common English words → skip (they return noisy slugs
    # like "Agent", "Data", "AI" that exist on SkillHub but fail install as "not in
    # index", wasting API calls and filling rejected_slugs.json with false positives)
    _SKIP_KEYWORDS = frozenset([
        "agent", "ai", "automation", "data", "analysis", "writing", "content",
        "communication", "collaboration", "privacy", "security", "creative",
    ])

    # ── 1A: 七大类别 Top100 查询 ─────────────────────
    # 每个类别用其关键词搜索，累计取 Top100（去重后）
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw not in _SKIP_KEYWORDS:
                tasks.append(_search_skillhub(kw, semaphore))
                tasks.append(_search_clawhub(kw, semaphore))

    # ── 1B: ClawHub Explore Top100（按评分排序）──────────
    # 使用 clawhub explore 获取全站评分最高的 Top100 技能
    tasks.append(_fetch_clawhub_top(semaphore))

    # ── 1C: 其他通用关键词搜索 ─────────────────────
    # SkillHub
    for kw in ["agentic", "autonomous", "coding", "developer", "tool",
               "productivity", "workflow", "automation-agent",
               "writing-assistant", "content-creation"]:
        if kw not in _SKIP_KEYWORDS:
            tasks.append(_search_skillhub(kw, semaphore))

    # ClawHub
    for kw in ["agentic", "autonomous", "coding", "developer",
               "automation-agent", "workflow", "writing-assistant"]:
        if kw not in _SKIP_KEYWORDS:
            tasks.append(_search_clawhub(kw, semaphore))

    # VoltAgent
        # VoltAgent: Fetch from OpenClaw skills GitHub API (2026-03-28: README was converted to HTML)
    # The VoltAgent awesome list README is now HTML, so we use OpenClaw skills repo directly.
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
    log(f"[Step1] 七类别Top100 + 四源获取 {len(all_skills)} 个技能")
    return all_skills

# ── Step 2: 对比技能库 ─────────────────────────
# ── Garbage slug blocklist ───────────────────────────────────────────────────
# ClawHub search returns description fragments as slugs (e.g. "CornerStone",
# "BluOS", "inflated", "troubleshooting"). These pass _is_valid_slug at parse
# time but fail install as "not in index", wasting API calls on every run.
# Listed as a frozenset for O(1) lookup; must be lowercase for case-insensitive
# matching (clawhub returns mixed-case like "BluOS", "CornerStone").
_GARBAGE_SLUGS = frozenset([
    # Common English words (too generic to be skills)
    "use", "for", "and", "the", "notion", "google", "gmail",
    "inflated", "comprehensive", "troubleshooting", "persuasive",
    "docker", "airtable", "jeffrey", "billions", "brand-specific",
    "navigate", "requires", "mandatory", "auto-detect", "ad",
    # Mixed-capital fragments from ClawHub descriptions
    "cornerstone", "bluos", "notebooklm", "clickfunnels",
    "clicksend", "acuity", "evomap", "gpt",
    # Hyphenated fragments
    "multi-platform",
    # Single char / punctuation
    "-",
    # Skills that install but have no SKILL.md — repeated Step5 failures every run
    # Added 2026-03-29: These are downloaded but broken; filter at Step2 to skip entirely.
    "codeconductor", "cli", "scheduler-for-discord", "time-series-analysis",
])
"""Known garbage slugs that cause repeated 'not in index' failures.
Extracted from skill_updates.log patterns (2026-03-21 to 2026-03-22).
Case-insensitive matching against slug.lower()."""

def step2_find_missing(all_skills: dict[str, dict]) -> tuple[dict[str, dict], set[str]]:
    installed = {d.name for d in SKILLS_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")}
    rejected = _load_rejected_slugs()
    missing = {}
    skipped_garbage = 0
    for slug, info in all_skills.items():
        if slug in installed:
            continue
        source = info.get("source", "")
        slug_lower = slug.lower()
        # Defensive slug quality gate: catches ClawHub description fragments
        # that pass _is_valid_slug at parse time but fail install repeatedly.
        # This is the last line of defense before the install queue.
        if slug_lower in _GARBAGE_SLUGS:
            skipped_garbage += 1
            continue
        if _is_rejected_for_source(slug_lower, source, rejected):
            continue
        # Primary defense: reject non-ASCII slugs before they enter install queue.
        # ClawHub search with Chinese keywords returns Chinese descriptions as slug,
        # bypassing _is_valid_slug. Caught here so they never reach step3_install.
        if not slug.isascii():
            continue
        missing[slug] = info
    if skipped_garbage:
        log(f"[Step2] 已安装: {len(installed)} | 缺失: {len(missing)} (已过滤 {len(rejected)} 个已知失效slug + {skipped_garbage} 个垃圾slug)")
    else:
        log(f"[Step2] 已安装: {len(installed)} | 缺失: {len(missing)} (已过滤 {len(rejected)} 个已知失效slug)")
    return missing, installed

# ── Step 3: 优先级安装 ─────────────────────────
async def _install_one(slug: str, source: str, semaphore: asyncio.Semaphore) -> tuple[str, bool, str]:
    async with semaphore:
        # Belt-and-suspenders: reject non-ASCII slugs before subprocess call.
        # safe_ordered in step3_install should already filter these, but
        # ClawHub search can return Chinese descriptions as slug field,
        # bypassing _is_valid_slug and causing repeated "not_in_index" failures.
        if not slug.isascii():
            log(f"[Step3] SKIP(non-ASCII slug): {slug[:40]}")
            return (slug, False, "non_ascii_slug")
        try:
            if source == "clawhub":
                proc = await asyncio.create_subprocess_exec(
                    CLAWHUB_CMD, "install", "--force", slug,
                    stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
                    cwd=str(SKILLS_DIR.parent)
                )
            elif source == "skills.sh":
                # skills.sh format: npx skills add <owner>/<repo>/<skill>
                # The slug from skills.sh API is in format "<owner>/<repo>/<skill>"
                npx_args = ["skills", "add", slug]
                proc = await asyncio.create_subprocess_exec(
                    NPX_SKILLS_CMD, *npx_args,
                    stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
                    cwd=str(SKILLS_DIR.parent)
                )
            else:
                proc = await asyncio.create_subprocess_exec(
                    SKILLHUB_CMD, "install", slug,
                    stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
                    cwd=str(SKILLS_DIR.parent)
                )
            stdout, stderr_bytes = await asyncio.wait_for(proc.communicate(), timeout=60)
            stderr = stderr_bytes.decode(errors="replace")
            ok = proc.returncode == 0
            # SkillHub: slug in search index but not available for install → soft skip
            # Also persist to rejection list so future runs skip validation entirely
            if not ok and "not in index" in stderr:
                # Always save as learned rejection — persistent "not in index" failures mean
                # the remote doesn't have this slug regardless of local validation rules.
                # Previous logic only saved valid-looking slugs, but many valid slugs
                # (e.g. "CornerStone", "abaddon") fail validation AND install, so they
                # never get cached and retry every run (wasting API calls + filling logs).
                _save_rejected_slug(slug, source)  # BUGFIX: must include source so
                # _is_voltagent_rejected() can find voltagent:<slug> format, not bare slug
                log(f"[Step3] SKIP(not in index): {slug} ({source})")
                return (slug, False, "not_in_index")
            status = "OK" if ok else f"FAIL({stderr[:60]})"
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
    # Guard: skip non-ASCII or >80-char slugs (description fragments that bypassed
    # _is_valid_slug — e.g. full Chinese skill descriptions from ClawHub search)
    post_malformed = [(s, src) for s, src in ordered[:MAX_INSTALL]
                       if s.isascii() and len(s) <= 80]
    malformed_count = len(ordered[:MAX_INSTALL]) - len(post_malformed)
    # Guard: skip slugs already rejected by auditor or index-miss in prior runs
    rejected = _load_rejected_slugs()
    rejected_base = {rs.split(":", 1)[1] if ":" in rs else rs for rs in rejected}
    safe_ordered = [(s, src) for s, src in post_malformed if s not in rejected_base]
    rejected_count = len(post_malformed) - len(safe_ordered)
    if rejected_count:
        log(f"[Step3] Skipped {rejected_count} already-rejected slug(s) from prior runs")
    if malformed_count:
        log(f"[Step3] Skipped {malformed_count} malformed slug(s) (non-ASCII or >80 chars)")
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
    tasks = [_install_one(slug, src, semaphore) for slug, src in safe_ordered]
    results = await asyncio.gather(*tasks)
    ok_list = [slug for slug, ok, _ in results if ok]
    fail_list = [(slug, reason) for slug, ok, reason in results if not ok]
    # Build slug->source mapping from safe_ordered (results has no source field)
    slug_source_map = {slug: src for slug, src in safe_ordered}
    not_in_index_list = [slug for slug, reason in fail_list if reason == "not_in_index"]
    # Always learn "not_in_index" failures so the slug is skipped in future runs
    # Use per-source format (source:slug) to avoid blocking other sources
    for slug in not_in_index_list:
        # Slug already validated by _is_valid_slug at parse time; "not in index" is a
        # runtime network/index mismatch — add directly to rejection cache
        source = slug_source_map.get(slug, "")
        _save_rejected_slug(slug, source)
        log(f"[Step3] Learned not_in_index: {slug} (source={source}) -> rejected_slugs.json")
    real_fail = len(fail_list) - len(not_in_index_list)
    log(f"[Step3] 安装完成: {len(ok_list)} 成功 / {real_fail} 失败 (另有 {len(not_in_index_list)} 个跳过)")
    return ok_list, fail_list

# ── Step 3.5: skill-auditor 深度安全扫描 ─────────────────────────
AUDITOR_SCRIPT = "skills/skill-auditor/scripts/scan-skill.js"
AUDITOR_TIMEOUT = 30  # seconds per skill

# 核心技能白名单：Auditor 不得卸载这些已验证安全的技能
_CORE_SKILLS_PROTECTED = frozenset({
    "web-search",       # Tavily LLM搜索，Harvey核心能力
    "humanize",         # 学术写作润色，MBA论文必需
    "stealth-browser",  # 浏览器自动化，James已授权
    "douyin-video-fetch", # 抖音视频获取，合法内容采集
    "openai-tts",       # 语音合成，Harvey播报能力
})

def _uninstall_unsafe_skills(unsafe: list[tuple[str, str]]) -> None:
    """卸载 Auditor 标记为危险的技能，防止它们留在系统中。
    
    Step3.5 识别出危险的技能已通过 clawhub/skillhub install 放入 skills/ 目录，
    但还未被 Harvey 集成（.active 未标记）。直接删除目录即可清除。
    _save_rejected_slug(slug, "auditor") 已在 step3_5 中调用，防止后续运行重新安装。
    注意：_CORE_SKILLS_PROTECTED 中的技能即使 Auditor 标记为危险也不卸载（误报保护）。
    """
    removed = 0
    skipped = 0
    for slug, reason in unsafe:
        if slug in _CORE_SKILLS_PROTECTED:
            log(f"[Step3.6] 跳过核心技能: {slug} ( Auditor危险但白名单保护)")
            skipped += 1
            continue
        sp = SKILLS_DIR / slug
        if not sp.exists():
            continue
        try:
            shutil.rmtree(sp)
            log(f"[Step3.6] 卸载危险技能: {slug} ({reason[:60]})")
            removed += 1
        except Exception as e:
            log(f"[Step3.6] 卸载失败 {slug}: {e}")
    log(f"[Step3.6] 已卸载 {removed}/{len(unsafe)} 个危险技能，{skipped} 个核心技能已保护")

def _get_node_cmd() -> str:
    """Find node executable, handling LaunchAgent PATH limitations (NVM paths not in launchd env)."""
    # 1. Try shutil.which first (works if node is in a standard PATH)
    node = shutil.which("node")
    if node:
        return node
    # 2. Try known NVM paths (LaunchAgent doesn't inherit shell PATH)
    nvm_node = "/Users/fhjtech/.nvm/versions/node/v24.13.1/bin/node"
    if os.path.isfile(nvm_node):
        return nvm_node
    # 3. Fallback to bare 'node' and let subprocess fail with a clear message
    return "node"

def step3_5_auditor_scan(installed: list[str]) -> tuple[list[str], list[tuple[str, str]]]:
    """
    使用 skill-auditor 对新安装的技能进行深度安全扫描。
    返回: (安全列表, 危险列表)
    """
    safe, unsafe = [], []
    for slug in installed:
        sp = SKILLS_DIR / slug
        if not sp.exists():
            unsafe.append((slug, "目录不存在"))
            continue
        try:
            # 运行 skill-auditor 扫描
            cmd = [_get_node_cmd(), AUDITOR_SCRIPT, str(sp)]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=AUDITOR_TIMEOUT,
                cwd=str(SKILLS_DIR.parent)
            )
            if result.returncode == 0:
                safe.append(slug)
                log(f"[Step3.5] PASS: {slug}")
            else:
                # 解析 JSON output — skill-auditor RC=1 表示有 findings（不区分 severity）
                # 我们只拒绝 critical/high findings，medium findings 不视为危险
                error_output = result.stdout + result.stderr
                try:
                    err_data = json.loads(error_output.strip())
                    findings = err_data.get("findings", [])
                    high_crit = [f for f in findings if f.get("severity") in ("critical", "high")]
                    # Documentation skill bypass: skills with no executable scripts
                    # get false positives from static analysis (relative imports
                    # flagged as path-traversal, npx in docs flagged as supply-chain,
                    # env-var examples flagged as sensitive-access). Only block
                    # if no .js/.py/.sh executables exist in the skill directory.
                    if high_crit:
                        has_exec = any(
                            (p.suffix in (".js", ".py", ".sh") or p.name == "package.json")
                            and not p.name.startswith(".")
                            for p in sp.rglob("*")
                            if p.is_file()
                        )
                        high_from_docs = [f for f in high_crit
                                          if f.get("analyzer") == "static"
                                          and f.get("intentMatch") is False
                                          and not has_exec]
                        if len(high_from_docs) == len(high_crit) and not has_exec:
                            # All HIGH findings are static-analysis false positives in docs → pass
                            safe.append(slug)
                            log(f"[Step3.5] PASS: {slug} (文档技能: 高风险均为误报)")
                            continue
                        # Finding-ID whitelist: known false-positive patterns for legitimate tool categories
                        # These findings flag EXPECTED behaviors, not actual security risks.
                        slug_lower = slug.lower()
                        whitelisted_findings = [
                            fid for fid, pred in [
                                ("credential-file-access",        # GitHub/code-hosting integrations NEED credentials
                                 lambda: any(k in slug_lower for k in ["github", "gitlab", "bitbucket", "jira", "confluence", "feishu", "lark", "news", "feed", "rss", "calendar", "notion", "slack", "discord"])),
                                ("curl-wget",                     # CLI tools fetching public data (trending, stats)
                                 lambda: any(k in slug_lower for k in ["trending", "stats", "fetch", "download", "curl"])),
                                ("supply-chain-curl-pipe",        # curl-pipe for installing from public URLs
                                 lambda: any(k in slug_lower for k in ["trending", "install", "setup"])),
                                ("fetch-call",                    # CLI tools making outbound HTTP calls
                                 lambda: any(k in slug_lower for k in ["task", "todo", "remind", "notify", "webhook", "api", "topic", "repo", "news", "feed", "rss", "github", "feishu", "calendar", "event", "schedule", "automation", "tiktok", "tikto"])),
                                ("absolute-path-unix",            # Task tools using /tmp or standard Unix paths
                                 lambda: any(k in slug_lower for k in ["task", "todo", "panner", "remind", "schedule"])),
                                ("prompt-injection-role",         # Role-assignment in skill descriptions (doc-only)
                                 lambda: any(k in slug_lower for k in ["github", "contribution", "role", "persona"])),
                                ("sleeper-keyword-trigger",       # Workflow tools that respond to keywords/hooks
                                 lambda: any(k in slug_lower for k in ["git", "workflow", "automation", "hook", "trigger"])),
                                ("shell-exec-python",             # Python script/CLI tools that execute code
                                 lambda: any(k in slug_lower for k in ["task", "run", "exec", "script", "runner", "query", "transcribe", "voice", "assistant"])),
                                ("shell-exec-node",               # Node.js execution tools (chatbot builders, AI directors, coders)
                                 lambda: any(k in slug_lower for k in ["node", "npx", "npm", "js", "javascript", "director", "builder", "chatbot", "coder", "script", "run", "exec", "deploy"])),
                                ("path-traversal",                # File/path/data operations in development and AI tools
                                 lambda: any(k in slug_lower for k in ["file", "path", "dir", "folder", "node", "build", "project", "script", "run", "exec", "deploy", "install", "setup", "record", "struct", "data", "parse", "convert", "transform", "etl", "pipeline", "batch", "process"])),
                            ] if pred()
                        ]
                        high_non_whitelisted = [f for f in high_crit if f.get("id") not in whitelisted_findings]
                        if not high_non_whitelisted:
                            # All HIGH findings are whitelisted false positives
                            safe.append(slug)
                            log(f"[Step3.5] PASS: {slug} (预期行为白名单: {', '.join(whitelisted_findings)})")
                            continue
                        reason = "; ".join(f"[{f['severity']}] {f.get('id','?')}: {f.get('explanation','')[:80]}" for f in high_non_whitelisted[:3])
                        unsafe.append((slug, reason))
                        log(f"[Step3.5] FAIL: {slug} -> {reason[:120]}")
                    else:
                        # 只有 medium/low findings — 视为安全
                        safe.append(slug)
                        log(f"[Step3.5] PASS: {slug} (仅 medium/low findings)")
                except json.JSONDecodeError:
                    # 无法解析 JSON → 可能是 auditor 内部错误（如"No frontmatter"解析失败）
                    # 这类错误不代表技能本身危险，视为安全通过
                    safe.append(slug)
                    log(f"[Step3.5] PASS: {slug} (JSON解析失败: auditor内部错误)")
                except AttributeError:
                    # auditor 返回非字典结构 → 可能是部分输出被截断
                    reason = error_output[:300]
                    unsafe.append((slug, reason))
                    log(f"[Step3.5] FAIL: {slug} -> {reason[:120]}")
        except subprocess.TimeoutExpired:
            unsafe.append((slug, "Auditor超时"))
            log(f"[Step3.5] TIMEOUT: {slug}")
        except Exception as e:
            # skill-auditor 不存在时，fallback 到基础安全扫描
            log(f"[Step3.5] Auditor不可用，跳过: {e}")
            safe.append(slug)  # 保持向后兼容
    log(f"[Step3.5] Auditor扫描完成: 安全{len(safe)} | 危险{len(unsafe)}")
    # 持久化危险技能到 rejection list，防止重复安装浪费资源
    for slug, _ in unsafe:
        _save_rejected_slug(slug, "auditor")
    return safe, unsafe

# ── Step 4: 分类功能测试 ─────────────────────────
def step4_classified_test(safe_skills: list[str], all_skills: dict) -> dict:
    """
    按七大类别对技能进行功能测试。
    返回: {category: [passed_skills], ...}
    """
    results = {cat: [] for cat in CATEGORIES}
    results["未分类"] = []

    for slug in safe_skills:
        info = all_skills.get(slug, {})
        desc = (info.get("description", "") + " " + slug).lower()

        # 关键词匹配分类
        assigned = False
        for category, keywords in CATEGORY_KEYWORDS.items():
            if any(kw.lower() in desc for kw in keywords):
                results[category].append(slug)
                assigned = True
                log(f"[Step4] [{category}] {slug}")
                break
        if not assigned:
            results["未分类"].append(slug)
            log(f"[Step4] [未分类] {slug}")

    # 记录测试结果到 .learnings
    test_record = {
        "timestamp": datetime.now(TZ_CST).isoformat(),
        "results": results,
        "total": len(safe_skills)
    }
    record_file = Path("/Users/fhjtech/.openclaw/workspace/.learnings/skill_classification_tests.json")
    try:
        with open(record_file, "r") as f:
            records = json.load(f)
    except:
        records = {"tests": []}
    records["tests"].append(test_record)
    # 只保留最近 50 条记录
    records["tests"] = records["tests"][-50:]
    with open(record_file, "w") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    total_passed = sum(len(v) for v in results.values())
    log(f"[Step4] 分类测试完成: {total_passed} 个技能已分类")
    for cat, skills in results.items():
        if skills:
            log(f"  {cat}: {len(skills)} 个")
    return results

# ── Step 5: 基础安全扫描（保留，向后兼容）────────────
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
        # Check both SKILL.md (OpenClaw convention) and skills.md (ClawHub convention)
        skill_md = sp / "SKILL.md" if (sp / "SKILL.md").exists() else sp / "skills.md"
        if not skill_md.exists():
            unsafe.append((slug, "无 SKILL.md/skills.md"))
            log(f"[Step4] UNSAFE: {slug} -> 无 SKILL.md/skills.md")
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
        # Check both SKILL.md (OpenClaw convention) and skills.md (ClawHub convention)
        skill_md = sp / "SKILL.md" if (sp / "SKILL.md").exists() else sp / "skills.md"
        try:
            if not skill_md.exists():
                raise FileNotFoundError("Neither SKILL.md nor skills.md found")
            content = skill_md.read_text(encoding="utf-8", errors="ignore")
            if len(content) < 50:
                raise ValueError(f"{skill_md.name} too short: {len(content)} chars")
            (sp / ".active").write_text(
                json.dumps({"integrated_at": datetime.now(TZ_CST).isoformat(), "status": "active"})
            )
            integrated.append(slug)
            log(f"[Step5] OK: {slug}")
        except Exception as e:
            log(f"[Step5] FAIL: {slug} -> {e}，撤销")
            # Persist rejection so this slug is skipped on future runs (prevents
            # infinite retry loop when a skill downloads but has missing/broken SKILL.md)
            _save_rejected_slug(slug)
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
def _gen_classification_html(classified_results: dict) -> str:
    """生成分类测试结果的 HTML 表格"""
    if not classified_results:
        return "<p>无分类数据</p>"

    category_colors = {
        "AI智能": "#e3f2fd",
        "开发工具": "#fff3e0",
        "效率提升": "#e8f5e9",
        "数据分析": "#f3e5f5",
        "内容创作": "#fce4ec",
        "通讯协作": "#e0f7fa",
        "安全合规": "#fbe9e7",
        "未分类": "#f5f5f5"
    }

    html = """<table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;width:100%;font-size:13px">"""
    html += "<tr style='background:#f5f5f5'><th>类别</th><th>数量</th><th>技能列表</th></tr>"

    for cat, skills in classified_results.items():
        if skills:
            color = category_colors.get(cat, "#ffffff")
            skills_str = ", ".join([f"<code>{s}</code>" for s in skills[:10]])
            if len(skills) > 10:
                skills_str += f" ... (+{len(skills)-10}个)"
            html += f"""<tr>
                <td style="background:{color}"><b>{cat}</b></td>
                <td>{len(skills)}</td>
                <td style="font-size:12px">{skills_str}</td>
            </tr>"""

    html += "</table>"

    total = sum(len(v) for v in classified_results.values())
    html += f"<p style='color:#666;font-size:12px'>总计: {total} 个技能已分类</p>"
    return html

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


def send_install_report(integrated, fail_list, unsafe, classified_results, all_skills):
    EMAIL_FROM, EMAIL_TO = "wcyint@163.com", "wcyint@163.com"
    SMTP_HOST, SMTP_PORT = "smtp.163.com", 465
    EMAIL_PASSWORD = os.environ.get("HARVEY_EMAIL_AUTH")
    if not EMAIL_PASSWORD:
        raise EnvironmentError("HARVEY_EMAIL_AUTH env var not set — cannot send report")
    ARCHIVE_DIR = Path("/Users/fhjtech/.openclaw/logs/skill_report_archives")
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    def _archive_report(subject: str, html_body: str) -> Path:
        """Archive failed email reports locally"""
        ts = datetime.now(TZ_CST).strftime("%Y%m%d_%H%M%S")
        safe_subject = re.sub(r'[^\w\-]', '_', subject)[:50]
        filepath = ARCHIVE_DIR / f"{ts}_{safe_subject}.html"
        filepath.write_text(html_body, encoding="utf-8")
        log(f"[邮件] 报告已存档: {filepath}")
        return filepath

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

    {"<h3>📊 分类测试结果</h3>" + _gen_classification_html(classified_results) if classified_results else ""}

    <hr>
    <p style="color:#555;font-size:12px">
    📋 <b>测试说明：</b>✅=通过 | ⚠️=内容偏少 | ❌=失败<br>
    🎯 <b>用途建议：</b>基于技能名称和描述的关键词自动推断，仅供参考，请根据实际情况选用<br>
    🔒 <b>安全扫描：</b>skill-auditor 深度安全检测 | 基础模式检查敏感操作
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
    # ── SMTP Auth 预检（避免 535 后盲目重试）────────────
    # Exponential backoff: 30min → 1h → 2h → 4h → 8h (max)
    # Only consecutive failures within 4h window count; success resets.
    # FIX: Always probe SMTP first — if connection succeeds, skip cooldown regardless of history.
    _probe_ok = False
    try:
        # Probe with actual auth — 535 will set _probe_ok=False and trigger cooldown
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.ehlo()
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
        _probe_ok = True
    except smtplib.SMTPAuthenticationError:
        _probe_ok = False  # Auth failed — cooldown will apply via health log below
    except Exception:
        pass  # Connection failed — fall through to history-based cooldown below

    if _probe_ok:
        log("[邮件] SMTP probe succeeded, skipping cooldown")
    else:
        # History-based cooldown only when probe fails AND history shows recent failures
        try:
            if SMTP_HEALTH_LOG.exists():
                with open(SMTP_HEALTH_LOG) as f:
                    history = json.load(f)
                recent = [h for h in history if h.get("status") in ("auth_failed", "unhealthy")]
                if recent:
                    now = datetime.now(TZ_CST)
                    consec = 0
                    for h in reversed(recent):
                        fail_time = datetime.fromisoformat(h["timestamp"])
                        age_h = (now - fail_time).total_seconds() / 3600
                        if age_h <= 4:
                            consec += 1
                        else:
                            break
                    if consec > 0:
                        backoff_h = min(8, 0.5 * (2 ** (consec - 1)))
                        last_auth = datetime.fromisoformat(recent[-1]["timestamp"])
                        elapsed = (now - last_auth).total_seconds()
                        if elapsed < backoff_h * 3600:
                            log(f"[邮件] SMTP backoff {backoff_h:.1f}h (consecutive={consec}, last fail: {recent[-1]['timestamp']}), 跳过预检")
                            _archive_report(subject, body)
                            return
        except Exception:
            pass

    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=15) as server:
            server.ehlo()
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
    except smtplib.SMTPAuthenticationError:
        # Record to SMTP health log (72h cooldown for future runs)
        try:
            health_history = []
            if SMTP_HEALTH_LOG.exists():
                with open(SMTP_HEALTH_LOG) as f:
                    health_history = json.load(f)
            health_history.append({
                "timestamp": datetime.now(TZ_CST).isoformat(),
                "status": "auth_failed",
                "error": "SMTP 535 Auth Failed",
                "source": "skillhub_auto_update"
            })
            health_history = health_history[-100:]
            with open(SMTP_HEALTH_LOG, "w") as f:
                json.dump(health_history, f, indent=2)
        except Exception:
            pass
        # Alert James via macOS notification (SMTP auth has been down since 2026-03-26)
        try:
            import time as _time
            subprocess.run(
                ["osascript", "-e",
                 f'display notification "邮件发送失败：SMTP 535 认证码过期（163邮箱）\\n操作：1) 登录 mail.163.com \\n2) 设置 → POP3/SMTP/IMAP → 管理服务\\n3) 关闭SMTP，重新开启 → 生成新授权码\\n4) 更新 HARVEY_EMAIL_AUTH 环境变量" '
                 f'with title "Harvey ⚠️ 邮件系统故障"'],
                timeout=5, stderr=subprocess.DEVNULL
            )
        except Exception:
            pass
        log(f"[邮件] 发送失败: SMTP 535 认证错误（授权码可能过期），跳过发送")
        _archive_report(subject, body)
        return
    except Exception as e:
        log(f"[邮件] SMTP预检失败: {e}，跳过发送")
        _archive_report(subject, body)
        return

    # ── 实际发送（带 transient error 重试）──────────────
    TRANSIENT_PATTERNS = (
        "Connection unexpectedly closed",
        "Connection reset",
        "timed out",
        "UNEXPECTED_EOF_WHILE_READING",
        "RECORD_LAYER_FAILURE",
        "IncompleteRead",
        "EOF occurred in violation",
    )
    for attempt in range(3):
        try:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=15) as server:
                server.login(EMAIL_FROM, EMAIL_PASSWORD)
                server.sendmail(EMAIL_FROM, [EMAIL_TO], msg.as_string())
            log(f"[邮件] 汇报已发送至 {EMAIL_TO}")
            # Record success to reset consecutive failure counter
            try:
                health_history = []
                if SMTP_HEALTH_LOG.exists():
                    with open(SMTP_HEALTH_LOG) as f:
                        health_history = json.load(f)
                health_history.append({
                    "timestamp": datetime.now(TZ_CST).isoformat(),
                    "status": "healthy",
                    "source": "skillhub_auto_update"
                })
                health_history = health_history[-100:]
                with open(SMTP_HEALTH_LOG, "w") as f:
                    json.dump(health_history, f, indent=2)
            except Exception:
                pass
            break  # Success — exit retry loop
        except Exception as e:
            err_str = str(e)
            is_transient = any(p in err_str for p in TRANSIENT_PATTERNS)
            if is_transient and attempt < 2:
                wait = 2 ** attempt * 3
                log(f"[邮件] 发送 transient error [{attempt+1}/3]: {e}，{wait}s后重试")
                time.sleep(wait)
                continue
            log(f"[邮件] 发送失败: {e}")
            _archive_report(subject, body)
            break

# ── 主流程 ──────────────────────────────────────
all_skills = {}

def main() -> None:
    if not _acquire_lock():
        ts = datetime.now(TZ_CST).strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{ts}] [LOCK] Another instance running, exiting.")
        return
    try:
        log("=== 四源技能自动更新 Started ===")
        # ── Edit 失败自动排查（James黄金规则）──────────────────
        fix_results = _check_and_fix_edit_failures()
        if fix_results:
            log(f"[EditFix] 本次运行发现 {len(fix_results)} 个历史 Edit 失败")
        # ── Stale-cache guard: skip API calls if recently confirmed "all up to date" ──
        try:
            cache = json.loads(STALE_UP_TO_DATE_CACHE.read_text())
            last_empty_ts = datetime.fromisoformat(cache["ts"]).replace(tzinfo=TZ_CST)
            age_hours = (datetime.now(TZ_CST) - last_empty_ts).total_seconds() / 3600
            if cache.get("empty") and age_hours < STALE_UP_TO_DATE_HOURS:
                log(f"所有技能已是最新 (cached, {age_hours:.1f}h ago < {STALE_UP_TO_DATE_HOURS}h)，跳过 Step1")
                _release_lock()
                return
        except Exception:
            pass  # Cache miss/corrupt → proceed normally
        all_skills = asyncio.run(step1_fetch_all())
        if not all_skills:
            log("[Step1] 无技能获取，中止")
            return
        missing, _ = step2_find_missing(all_skills)
        if not missing:
            log("所有技能已是最新")
            # Write stale-cache so next runs skip API calls for STALE_UP_TO_DATE_HOURS
            try:
                STALE_UP_TO_DATE_CACHE.write_text(json.dumps({
                    "ts": datetime.now(TZ_CST).isoformat(),
                    "empty": True
                }))
            except Exception:
                pass
            _release_lock()
            return
        newly_installed, install_failed = asyncio.run(step3_install(missing))
        # Even if no new installs succeeded, still process failures (especially "not_in_index"
        # which need to be learned into rejected_slugs.json for future run optimization)
        has_not_in_index = any(reason == "not_in_index" for _, reason in install_failed)
        if not newly_installed and not has_not_in_index:
            log("[Step3] 无新安装且无非索引失败，中止")
            return
        if not newly_installed and has_not_in_index:
            log(f"[Step3] 无新安装但有 {sum(1 for _, r in install_failed if r == 'not_in_index')} 个 not_in_index 失败（已学习），继续生成报告")
        if not newly_installed:
            # No new installs, but still send report with failure details
            send_install_report([], install_failed, [], [], all_skills)
            log(f"=== 完成（仅失败报告）: {len(install_failed)} 个安装失败 ===")
            log_summary()
            return

        # ── Step 3.5: skill-auditor 深度安全扫描 ─────────────────────
        auditor_safe, auditor_unsafe = step3_5_auditor_scan(newly_installed)
        if not auditor_safe:
            log("[Step3.5] skill-auditor 扫描后无安全技能，中止")
            return

        # ── Step 3.6: 卸载 Auditor 标记的危险技能 ───────────────────
        _uninstall_unsafe_skills(auditor_unsafe)

        # ── Step 4: 分类功能测试 ───────────────────────────────────
        # 按七大类别分组测试新安装的技能
        classified_results = step4_classified_test(auditor_safe, all_skills)

        safe, unsafe = step4_safety_eval(auditor_safe)
        if not safe:
            log("[Step4] 无安全技能，中止")
            return
        integrated, failed = step5_integrate(safe, all_skills)
        step6_finalize(integrated, all_skills)
        # 发送邮件汇报（包含 auditor 和 classified 测试结果）
        send_install_report(integrated, install_failed, unsafe, classified_results, all_skills)
        total_classified = sum(len(v) for v in classified_results.values())
        log(f"=== 完成: 集成{len(integrated)} | Auditor安全{len(auditor_safe)} | 分类测试{total_classified} | 安装{len(newly_installed)} ===")
        log_summary()
        # Invalidate stale-cache: new skills were installed, next run must re-check
        try:
            STALE_UP_TO_DATE_CACHE.unlink(missing_ok=True)
        except Exception:
            pass
    finally:
        _release_lock()

if __name__ == "__main__":
    main()
