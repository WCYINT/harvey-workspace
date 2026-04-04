#!/usr/bin/env python3
"""
auto_learner.py - Harvey's Self-Evolving Learning System

Automatically captures errors, corrections, and insights → writes to .learnings/
Verification cron resolves pending entries and promotes high-value learnings.

Usage:
    python3 auto_learner.py --log-error "description" --error-details "..." --area infra
    python3 auto_learner.py --log-learning "what was learned" --category correction
    python3 auto_learner.py --verify          # Run verification: resolve pending items
    python3 auto_learner.py --report         # Generate pending items report
    python3 auto_learner.py --stats          # Show learning statistics
    python3 auto_learner.py --auto-capture   # Called by cron to auto-capture recent errors
"""

import os
import sys
import json
import re
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

WORKSPACE = Path.home() / ".openclaw" / "workspace"
LEARNINGS_DIR = WORKSPACE / ".learnings"
SCRIPTS_DIR = WORKSPACE / ".scripts"
LOGS_DIR = Path.home() / ".openclaw" / "logs"

# ─── ID generation ───────────────────────────────────────────────────────────

def tailn(file_path: Path, n: int = 200) -> list:
    """Read only the last n lines of a file without loading the entire file.
    
    Uses a rolling read-backwards approach: reads a conservative window from EOF,
    then trims to exactly n lines. Avoids O(n) line-counting for large files.
    """
    try:
        with open(file_path, "rb") as fh:
            total_size = fh.seek(0, 2)
            if total_size <= 0:
                return []
            # Read a window: n lines * 2000 bytes (worst-case markdown+code line) + 2KB buffer.
            # LEARNINGS.md entries contain code blocks, tables, URLs — lines can be 1KB-100KB.
            # Small files (window > total): min() returns total → read all → lines[-n:] works
            # Large files (window < total): min() returns n*2000+2048 → seek from EOF backward
            # NOTE: If a single line exceeds this window (e.g. 100KB URL on one line),
            # splitlines() includes the truncated fragment, losing recent entries at boundary.
            # This is a known limitation of the read-backwards approach; 2000 multiplier is a
            # practical balance between memory usage and coverage for typical markdown files.
            window_size = min(total_size, n * 2000 + 2048)
            fh.seek(max(0, total_size - window_size))
            remaining = fh.read()
            # For large files, the seek position may land mid-line, causing the
            # first "line" from splitlines() to be a partial fragment. Detect this
            # and expand the window until we have at least n complete lines.
            # The previous code dropped the partial line silently, losing recent
            # entries at the window boundary (bug: entry IDs and content truncated).
            max_window = total_size  # never read more than the whole file
            while True:
                decoded = remaining.decode("utf-8", errors="ignore")
                lines = decoded.splitlines()
                # Count how many lines in the window are complete (non-partial).
                # A line is partial if the window doesn't start at file beginning
                # AND the first char is not '\n' (we started mid-line).
                started_mid = (total_size - window_size) > 0
                is_partial_first = started_mid and decoded and decoded[0] not in ("\n", "\r")
                num_complete = len(lines) - (1 if is_partial_first else 0)
                if num_complete >= n or window_size >= max_window:
                    # Have enough lines OR have read entire file; return what we have.
                    if is_partial_first and num_complete >= n:
                        # Skip partial first line, then take last n complete lines
                        return lines[len(lines) - n:]
                    elif is_partial_first:
                        # Not enough complete lines; return all complete lines
                        return lines[1:]
                    else:
                        return lines[-n:]
                # Expand window and re-read to capture more complete lines
                window_size = min(max_window, window_size * 2)
                fh.seek(max(0, total_size - window_size))
                remaining = fh.read()
    except Exception:
        return []


def generate_id(prefix: str) -> str:
    """Generate sequential ID like ERR-20260326-001.
    
    IDs are at file bottom (recent entries), so read LAST 200 lines only.
    Uses tailn() to avoid loading large files into memory.
    """
    date_str = datetime.now().strftime("%Y%m%d")
    pattern = f"{prefix}-{date_str}"
    counter = 1
    for f in LEARNINGS_DIR.glob("*.md"):
        # Read only last 200 lines - IDs are at bottom of each file (recent entries)
        lines = tailn(f, 200)
        for line in lines:
            m = re.match(rf"## \[{pattern}-(\d+)\]", line)
            if m:
                counter = max(counter, int(m.group(1)) + 1)
    return f"{pattern}-{counter:03d}"


# ─── File operations ────────────────────────────────────────────────────────

def ensure_learnings_dir() -> None:
    """Ensure .learnings directory exists with required files."""
    LEARNINGS_DIR.mkdir(parents=True, exist_ok=True)
    for name in ["ERRORS.md", "LEARNINGS.md", "FEATURE_REQUESTS.md"]:
        p = LEARNINGS_DIR / name
        if not p.exists():
            p.write_text(f"# {name.replace('.md','')}\n\n"
                         "Command failures, exceptions, and unexpected behavior.\n\n"
                         "**Areas**: frontend | backend | infra | tests | docs | config\n"
                         "**Statuses**: pending | in_progress | resolved | wont_fix\n\n---\n\n")


def append_entry(file_path: Path, content: str) -> None:
    """Append entry to a learnings file."""
    ensure_learnings_dir()
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(content + "\n\n---\n\n")


def count_pending(pattern: str = "pending") -> dict:
    """Count pending/in_progress entries across all learnings files.
    Only matches **Status**: <pattern> (not body fields like **Pending**:).
    """
    counts = {}
    for name in ["ERRORS.md", "LEARNINGS.md", "FEATURE_REQUESTS.md"]:
        p = LEARNINGS_DIR / name
        if p.exists():
            text = p.read_text()
            # Match lines: **Status**: <pattern> (only Status field, not body **Pending**:)
            counts[name] = len(re.findall(
                rf"^\*\*Status\*\*:\s+{pattern}\b",
                text,
                re.IGNORECASE | re.MULTILINE
            ))
    return counts


# ─── Entry builders ─────────────────────────────────────────────────────────

def build_error_entry(
    summary: str,
    error_details: str,
    area: str = "backend",
    command: str = "",
    context: str = "",
    reproducible: str = "unknown",
) -> str:
    """Build a formatted error entry."""
    entry_id = generate_id("ERR")
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")
    # Add +08:00 suffix if not present
    if not now.endswith("+0800") and not re.search(r"[+-]\d{4}$", now):
        now = now + "+08:00"
    
    ctx_parts = []
    if command:
        ctx_parts.append(f"- Command: `{command}`")
    if context:
        ctx_parts.append(f"- Context: {context}")
    
    content = f"""## [{entry_id}] {area}

**Logged**: {now}
**Priority**: high
**Status**: pending
**Area**: {area}

### Summary
{summary}

### Error
```
{error_details[:4000]}
```

### Context
{chr(10).join(ctx_parts) if ctx_parts else "- (none provided)"}

### Suggested Fix
_Not yet determined — run verification to identify root cause._

### Metadata
- Reproducible: {reproducible}
- Source: auto_learner.py
"""
    return content


def build_learning_entry(
    summary: str,
    details: str,
    category: str = "insight",
    area: str = "backend",
    priority: str = "medium",
    suggested_action: str = "",
    source: str = "auto_capture",
) -> str:
    """Build a formatted learning entry."""
    entry_id = generate_id("LRN")
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")
    if not re.search(r"[+-]\d{4}$", now):
        now = now + "+08:00"
    
    content = f"""## [{entry_id}] {category}

**Logged**: {now}
**Priority**: {priority}
**Status**: pending
**Area**: {area}

### Summary
{summary}

### Details
{details}

### Suggested Action
{suggested_action or "_Not yet determined."}

### Metadata
- Source: {source}
- Category: {category}
"""
    return content


# ─── Verification engine ─────────────────────────────────────────────────────

def get_recent_errors(minutes: int = 30) -> list:
    """Get recent errors from gateway and cron logs."""
    errors = []
    log_files = list(LOGS_DIR.glob("*.log")) if LOGS_DIR.exists() else []
    
    for lf in sorted(log_files, key=lambda p: p.stat().st_mtime, reverse=True)[:5]:
        try:
            # gateway.err.log has very long lines (model-fallback entries ~300-500 bytes);
            # use 2000-line window to ensure ~6h of lookback covers the 60-min capture window.
            n_lines = 2000 if "gateway.err.log" in lf.name else 500
            lines = tailn(lf, n_lines)
            text = "\n".join(lines)
            # Look for error patterns
            for m in re.finditer(
                # Timestamp: allow optional .sss and timezone so \D* stops at the [source] space.
                # Without .sss: \D*=.316+08:00 and eats the [source] space → \s* fails.
                r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?[^\sT]*)\s+\[([^\]]+)\]\s*.*?(?:ERROR|error|Error|failed|Failed|FAILED|Exception|Traceback).*?(?=\n\d{4}-|$)",
                text,
                re.DOTALL | re.IGNORECASE,
            ):
                ts = m.group(1).strip()[:25]  # Keep full ISO-8601 with timezone: "2026-04-01T02:08:00+08:00" (25 chars)
                err_text = m.group(0).strip()[:500]
                # Broaden filter: catch subprocess failures + Python exceptions + HTTP errors.
                # Previously only caught subprocess/signal → missed all Python tracebacks.
                if any(x in err_text for x in [
                    "SIGTERM", "SIGKILL", "signal", "exec failed", "subprocess",
                    "NameError", "TypeError", "KeyError", "ValueError",
                    "ImportError", "AttributeError", "RuntimeError",
                    "HTTPError", "ConnectionError", "TimeoutError",
                    "401", "Unauthorized",  # supermemory plugin auth failures
                ]):
                    errors.append({"timestamp": ts, "error": err_text, "file": lf.name})
        except Exception:
            pass
    
    return errors


def get_skill_update_failures(minutes: int = 180) -> list:
    """Get real failures from skill_updates.log (SMTP, install failures).

    Ignores slug-validation noise. Only captures:
    - SMTP 535 auth errors
    - Installation failures (X 成功 / Y 失败 where Y > 0)
    """
    skill_log = LEARNINGS_DIR / "skill_updates.log"
    if not skill_log.exists():
        return []

    try:
        lines = tailn(skill_log, 500)
    except Exception:
        return []

    cutoff = datetime.now() - timedelta(minutes=minutes)
    failures = []

    # Parse all lines once; build list of (ts, line) for entries within the cutoff window.
    # (Avoids reversing twice and prevents early-break from skipping failures that
    # appear after an old entry in reversed order.)
    recent = []
    for line in lines:
        ts_match = re.match(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]", line)
        if not ts_match:
            continue
        try:
            ts = datetime.strptime(ts_match.group(1), "%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
        if ts >= cutoff:
            recent.append((ts, line))

    # Process newest-first so we capture the most recent failures first
    for ts, line in sorted(recent, reverse=True):
        ts_match = re.match(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]", line)

        # Real failure: SMTP 535
        if "SMTP 535" in line or "认证错误" in line:
            failures.append({
                "timestamp": ts_match.group(1),
                "error": f"[skill_updates.log] {line.strip()}",
                "file": "skill_updates.log"
            })
            continue

        # Real failure: catastrophic install failures (≥50% failed — partial failures are normal)
        m = re.search(r"\[Step3\]\s*安装完成:\s*(\d+)\s*成功\s*/\s*(\d+)\s*失败", line)
        if m:
            success = int(m.group(1))
            failure = int(m.group(2))
            # Only capture when failure rate >= 50%; normal partial failures (e.g. 1/15) are expected
            if failure >= success:
                failures.append({
                    "timestamp": ts_match.group(1),
                    "error": f"[skill_updates.log] Install failure: {success} OK / {failure} failed",
                    "file": "skill_updates.log"
                })

    return failures


def resolve_entry(file_path: Path, entry_id: str, resolution: str, notes: str = "") -> bool:
    """Mark an entry as resolved with resolution notes."""
    text = file_path.read_text()
    pattern = rf"(## \[{entry_id}\].*?)(### Metadata\n)(.*?)((?:---\n\n|$))"
    
    def make_resolved(m) -> str:
        inner = m.group(1)
        inner = re.sub(r"\*\*Status\*\*.*?\n", "**Status**: resolved\n", inner)
        now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
        resolved_block = f"\n### Resolution\n- **Resolved**: {now}\n- **Notes**: {notes or resolution}\n"
        # m.group(1)=header, (2)='### Metadata\n', (3)=metadata-content, (4)=---\n\n or end
        return inner + m.group(2) + m.group(3) + resolved_block + (m.group(4) if m.group(4) else "")
    
    new_text = re.sub(pattern, make_resolved, text, flags=re.DOTALL)
    if new_text != text:
        file_path.write_text(new_text)
        return True
    return False


def auto_resolve_simple(errors: list) -> int:
    """Attempt to auto-resolve entries with known fixes.
    
    Bug fix (2026-03-29): Previously matched by ID prefix (e.g. "ERR-2026032" matches
    ALL March errors) then applied the same fix to ALL — scope creep bug.
    Now matches by BOTH: entry's summary text must contain the keyword AND ID prefix.
    """
    resolved_count = 0

    # Known fix mappings: keyword → (ID prefix, fix action)
    # Only auto-resolve if the pending entry's summary ALSO mentions the keyword.
    known_fixes = {
        "SMTP": ("ERR-2026032", "SMTP credentials issue - notify James to regenerate 163 authorization code"),
        "jiti": ("ERR-2026032", "jiti cache staleness - clear /tmp/jiti/ and restart gateway"),
        "Could not find the exact text": ("ERR-20260403", "jiti cache staleness - clear /tmp/jiti/ and restart gateway"),
        "duplicate tool_call": ("ERR-2026032", "MiniMax API tool_call ID collision - use fresh session per cron run"),
    }

    for err_info in errors[:5]:
        err_text = err_info.get("error", "")
        for keyword, (entry_prefix, fix) in known_fixes.items():
            if keyword.lower() not in err_text.lower():
                continue
            # Find pending entries whose ID matches the prefix AND summary mentions the keyword
            for f in LEARNINGS_DIR.glob("*.md"):
                text = f.read_text()
                for m in re.finditer(r"## \[(ERR-\d+-\w+)\]", text):
                    eid = m.group(1)
                    if not eid.startswith(entry_prefix):
                        continue
                    # Extract entry body to check if summary mentions the keyword
                    start = m.start()
                    next_entry = text.find("\n## ", start + 1)
                    entry_body = text[start:next_entry if next_entry > 0 else len(text)]
                    if keyword.lower() not in entry_body.lower():
                        continue
                    # Check if still pending
                    status_pos = text.find("**Status**:", start)
                    if status_pos < 0:
                        continue
                    status_line_end = text.find("\n", status_pos)
                    status_val = text[status_pos:status_line_end]
                    if "pending" not in status_val.lower():
                        continue
                    if resolve_entry(f, eid, fix, "Auto-resolved by verification engine"):
                        resolved_count += 1

    return resolved_count


def promote_high_value_learning(entry_text: str, target_file: str, section: str) -> bool:
    """Promote a learning to AGENTS.md, SOUL.md, TOOLS.md, etc.
    
    Returns True if promoted, False if skipped (no match, already exists, or file not found).
    """
    # Extract the core principle
    decision_match = re.search(r"\*\*(Decision principle [^:]+)\*\*:\s*(.+)", entry_text)
    if not decision_match:
        return False
    
    key = decision_match.group(1)
    value = decision_match.group(2).strip()
    
    target_path = WORKSPACE / target_file
    if not target_path.exists():
        return False
    
    text = target_path.read_text()
    
    # Check if already promoted
    if key in text:
        return False
    
    # Add to appropriate section
    new_entry = f"\n### {key}\n{value}\n"
    
    # Find insertion point
    if section in text:
        idx = text.rfind(f"## {section}") 
        if idx < 0:
            idx = text.rfind(f"### {section}")
        if idx < 0:
            text += new_entry
        else:
            # Find end of this section
            next_section = text.find("\n## ", idx + 1)
            if next_section < 0:
                text += new_entry
            else:
                text = text[:next_section] + new_entry + text[next_section:]
    else:
        text += new_entry
    
    target_path.write_text(text)
    return True


# ─── Auto-capture from recent logs ──────────────────────────────────────────

def capture_recent_errors() -> str:
    """Called by cron to find and log new errors not yet in learnings."""
    # Gateway/cron logs + skill_updates.log
    errors = get_recent_errors(minutes=60)
    errors += get_skill_update_failures(minutes=180)
    if not errors:
        return "No new errors found in recent logs."
    
    captured = 0
    for err in errors[:3]:
        err_text = err["error"]
        
        # Deduplicate: strip timestamps/file-paths to get stable error pattern.
        # SMTP lines from skill_updates.log have format:
        #   [skill_updates.log] [YYYY-MM-DD HH:MM:SS] [邮件] ... SMTP 535 ...
        # The first 100 chars vary by timestamp, so we extract the stable part.
        dedup_pattern = err_text
        m = re.search(r"(SMTP 535[^]]+|Install failure: \d+ OK / \d+ failed)", err_text)
        if m:
            dedup_pattern = m.group(1)  # e.g. "SMTP 535 认证错误（授权码可能过期）"
        
        # Also strip the skill_updates.log prefix + timestamp if present
        dedup_pattern = re.sub(r"^\[skill_updates\.log\]\s*\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]\s*", "", dedup_pattern)
        
        # Check if already logged using stable pattern
        # Pre-load all learnings content once (avoid re-reading files in loop)
        if "_learnings_cache" not in globals():
            global _learnings_cache
            _learnings_cache = {}
            for lf in LEARNINGS_DIR.glob("*.md"):
                _learnings_cache[lf.name] = lf.read_text(errors="ignore")
        
        already_logged = dedup_pattern[:80] in "\n".join(_learnings_cache.values())
        
        if not already_logged:
            area = "infra"
            if "python" in err_text.lower() or ".py" in err_text:
                area = "backend"
            elif "git" in err_text.lower():
                area = "config"
            
            entry = build_error_entry(
                summary=f"Auto-captured error from {err['file']}",
                error_details=err_text,
                area=area,
                context=f"Source: {err['file']} at {err['timestamp']}",
            )
            append_entry(LEARNINGS_DIR / "ERRORS.md", entry)
            captured += 1
    
    return f"Captured {captured} new error(s) from recent logs."


# ─── Main commands ───────────────────────────────────────────────────────────

def cmd_log_error(args) -> None:
    """Log a new error."""
    entry = build_error_entry(
        summary=args.summary,
        error_details=args.error_details or "No details provided",
        area=args.area,
        command=args.command or "",
        context=args.context or "",
        reproducible=args.reproducible or "unknown",
    )
    append_entry(LEARNINGS_DIR / "ERRORS.md", entry)
    entry_id = re.search(r"## \[(ERR-\d+-\w+)\]", entry).group(1)
    print(f"Logged error: {entry_id}")
    return entry_id


def cmd_log_learning(args) -> None:
    """Log a new learning."""
    entry = build_learning_entry(
        summary=args.summary,
        details=args.details or args.summary,
        category=args.category,
        area=args.area,
        priority=args.priority,
        suggested_action=args.action or "",
        source=args.source or "manual",
    )
    append_entry(LEARNINGS_DIR / "LEARNINGS.md", entry)
    entry_id = re.search(r"## \[(LRN-\d+-\w+)\]", entry).group(1)
    print(f"Logged learning: {entry_id}")
    return entry_id


def cmd_verify(args) -> str:
    """Run verification: capture new errors, auto-resolve, report."""
    results = []
    
    # 1. Auto-capture recent errors
    capture_msg = capture_recent_errors()
    results.append(capture_msg)
    
    # 2. Get recent errors for resolution attempts
    errors = get_recent_errors(minutes=120)
    
    # 3. Attempt auto-resolution
    if errors:
        resolved = auto_resolve_simple(errors)
        results.append(f"Auto-resolved {resolved} entry/entries.")
    
    # 4. List all pending items
    counts = count_pending("pending")
    in_progress = count_pending("in_progress")
    
    pending_list = []
    for fname, cnt in counts.items():
        if cnt > 0:
            pending_list.append(f"  {fname}: {cnt} pending")
    
    if pending_list:
        results.append("Pending items:\n" + "\n".join(pending_list))
    else:
        results.append("No pending items — all clear!")
    
    return "\n".join(results)


def cmd_report(args) -> str:
    """Generate a detailed pending items report."""
    pending = []
    
    for name in ["ERRORS.md", "LEARNINGS.md", "FEATURE_REQUESTS.md"]:
        p = LEARNINGS_DIR / name
        if not p.exists():
            continue
        
        text = p.read_text()
        # Find all entries
        for m in re.finditer(r"(## \[[^\]]+\][^\n]*\n\*\*Logged\*\*: ([^\n]+)\n\*\*Status\*\*: ([^\n]+))", text):
            full = m.group(0)
            entry_id = re.search(r"## \[([^\]]+)\]", full).group(1)
            logged = m.group(2)
            status = m.group(3).strip()
            
            if "pending" in status.lower():
                summary_match = re.search(r"### Summary\n(.+?)(?=\n###|\n---\n|$)", full, re.DOTALL)
                summary = summary_match.group(1).strip()[:100] if summary_match else "(no summary)"
                pending.append({
                    "id": entry_id,
                    "file": name,
                    "logged": logged,
                    "summary": summary,
                })
    
    if not pending:
        return "No pending items. All learnings are resolved!"
    
    lines = [f"# Pending Items Report ({len(pending)} total)\n"]
    for i, item in enumerate(pending, 1):
        lines.append(f"{i}. [{item['id']}] ({item['file']})")
        lines.append(f"   Logged: {item['logged']}")
        lines.append(f"   {item['summary']}")
        lines.append("")
    
    return "\n".join(lines)


def cmd_stats(args) -> str:
    """Show learning statistics."""
    err_p = LEARNINGS_DIR / "ERRORS.md"
    learn_p = LEARNINGS_DIR / "LEARNINGS.md"
    feat_p = LEARNINGS_DIR / "FEATURE_REQUESTS.md"

    total_errors = resolved_errors = total_learnings = resolved_learnings = 0

    if err_p.exists():
        t = err_p.read_text()
        total_errors = len(re.findall(r"## \[ERR-", t))
        resolved_errors = len(re.findall(r"\*\*Status\*\*: resolved", t))

    if learn_p.exists():
        t = learn_p.read_text()
        total_learnings = len(re.findall(r"## \[LRN-", t))
        resolved_learnings = len(re.findall(r"\*\*Status\*\*: resolved", t))

    total_features = len(re.findall(r"## \[FEAT-", feat_p.read_text())) if feat_p.exists() else 0
    
    pending_errors = total_errors - resolved_errors
    pending_learnings = total_learnings - resolved_learnings
    
    return f"""# Harvey Learning Statistics

## Errors
  Total: {total_errors} | Resolved: {resolved_errors} | Pending: {pending_errors}

## Learnings
  Total: {total_learnings} | Resolved: {resolved_learnings} | Pending: {pending_learnings}

## Feature Requests
  Total: {total_features}

## Resolution Rate
  Errors: {f"{resolved_errors/total_errors*100:.0f}%" if total_errors else "N/A"}
  Learnings: {f"{resolved_learnings/total_learnings*100:.0f}%" if total_learnings else "N/A"}
"""


# ─── Pattern extraction ───────────────────────────────────────────────────────

def extract_patterns() -> str:
    """Extract decision principles + error signatures from learnings into patterns.json."""
    import json as _json

    patterns = {}
    error_sigs = {}
    
    # Extract Decision Principles from ERRORS.md
    err_text = (LEARNINGS_DIR / "ERRORS.md").read_text()
    for m in re.finditer(r"\*\*Decision principle \(([^)]+)\)\*\*:\s*(.+?)(?=\n###|\n\*\*|\n---)", err_text, re.DOTALL):
        key = m.group(1).strip()
        value = m.group(2).strip()
        patterns[key] = {
            "principle": key,
            "trigger": _extract_triggers(value),
            "fix": value,
            "prevention": value,
            "priority": "high"
        }
    
    # Extract Decision Principles from LEARNINGS.md
    lrn_text = (LEARNINGS_DIR / "LEARNINGS.md").read_text()
    for m in re.finditer(r"\*\*Decision principle \(([^)]+)\)\*\*:\s*(.+?)(?=\n###|\n\*\*|\n---)", lrn_text, re.DOTALL):
        key = m.group(1).strip()
        value = m.group(2).strip()
        if key not in patterns:
            patterns[key] = {
                "principle": key,
                "trigger": _extract_triggers(value),
                "fix": value,
                "prevention": value,
                "priority": "medium"
            }
    
    # Extract error signatures from ERRORS.md
    # Parse each ERR- entry and extract from Summary/Details/Root Cause sections
    for m in re.finditer(r"(## \[(ERR-\d+-\w+)\].*?)(?=## \[ERR-|\Z)", err_text, re.DOTALL):
        entry_full = m.group(1)
        entry_id = m.group(2)
        
        # Extract Summary
        sm = re.search(r"### Summary\n(.+?)(?=\n###|\n---)", entry_full, re.DOTALL)
        summary = sm.group(1).strip()[:300] if sm else ""
        
        # Extract Details/Root Cause
        dm = re.search(r"(?:### Details|### Root Cause|### Root cause)\n(.+?)(?=\n###|\n---)", entry_full, re.DOTALL)
        details = dm.group(1).strip()[:300] if dm else ""
        
        combined = (summary + " " + details).strip()
        
        if not combined:
            continue
        
        # Classify this error
        sig_key = _classify_error(combined)
        if sig_key and sig_key not in error_sigs:
            error_sigs[sig_key] = {
                "patterns": _extract_error_keywords(combined),
                "entry_prefix": entry_id[:12],
                "auto_fix": summary[:200] if summary else "Review entry and apply fix.",
                "summary": summary[:200] if summary else details[:200]
            }
    
    # Count resolution stats
    t = (LEARNINGS_DIR / "ERRORS.md").read_text()
    total_err = len(re.findall(r"## \[ERR-", t))
    resolved_err = len(re.findall(r"\*\*Status\*\*: resolved", t))
    
    output = {
        "version": "1.0",
        "generated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "source": "auto_learner.py --extract-patterns",
        "patterns": patterns,
        "error_signatures": error_sigs,
        "resolution_stats": {
            "total_errors": total_err,
            "resolved_errors": resolved_err,
            "resolution_rate": round(resolved_err/total_err, 2) if total_err else 0
        }
    }
    
    out_path = LEARNINGS_DIR / "patterns.json"
    out_path.write_text(_json.dumps(output, ensure_ascii=False, indent=2))
    
    return (f"Extracted {len(patterns)} decision principles + "
            f"{len(error_sigs)} error signatures → {out_path.name}")


def _extract_triggers(text: str) -> list:
    """Extract trigger keywords from a principle description."""
    keywords = []
    text_lower = text.lower()
    for kw in re.findall(r"[a-z_]+(?:_[a-z_]+){1,3}", text_lower):
        if len(kw) > 4 and kw not in ["this_is", "the_is"]:
            keywords.append(kw)
    return keywords[:6]


def _classify_error(text: str) -> str:
    """Classify error text into a signature key."""
    text_lower = text.lower()
    if "535" in text or "authentication failed" in text_lower or "smtp" in text_lower:
        return "SMTP_auth_failed"
    if "cannot find module" in text_lower or "plugin" in text_lower:
        return "jiti_module_not_found"
    if "duplicate tool_call" in text_lower or "2013" in text_lower:
        return "duplicate_tool_call_id"
    if "permission denied" in text_lower or "eacces" in text_lower:
        return "permission_denied"
    if "not found" in text_lower or "enoent" in text_lower:
        return "not_found"
    if "timeout" in text_lower:
        return "timeout"
    if "exit code" in text_lower:
        return "exit_code_nonzero"
    return None


def _extract_error_keywords(text: str) -> list:
    """Extract specific keyword patterns from error text."""
    keywords = []
    # Extract error codes/numbers
    for m in re.finditer(r"\b[A-Z]{2,}_[A-Z_]+\b|\b\d{3,}\b|\b[A-Za-z]+Error\b", text):
        val = m.group(0)
        if val not in keywords and len(val) > 2:
            keywords.append(val)
    return keywords[:8]


# ─── CLI entry point ─────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Harvey Auto-Learner")
    sub = parser.add_subparsers(dest="cmd")
    
    # log-error
    p_err = sub.add_parser("log-error", help="Log a new error")
    p_err.add_argument("--summary", required=True)
    p_err.add_argument("--error-details", default="")
    p_err.add_argument("--area", default="backend")
    p_err.add_argument("--command", default="")
    p_err.add_argument("--context", default="")
    p_err.add_argument("--reproducible", default="unknown")
    
    # log-learning
    p_lrn = sub.add_parser("log-learning", help="Log a new learning")
    p_lrn.add_argument("--summary", required=True)
    p_lrn.add_argument("--details", default="")
    p_lrn.add_argument("--category", default="insight")
    p_lrn.add_argument("--area", default="backend")
    p_lrn.add_argument("--priority", default="medium")
    p_lrn.add_argument("--action", default="")
    p_lrn.add_argument("--source", default="manual")
    
    # verify
    sub.add_parser("verify", help="Run verification engine")
    
    # report
    sub.add_parser("report", help="Generate pending items report")
    
    # stats
    sub.add_parser("stats", help="Show learning statistics")
    
    # auto-capture
    sub.add_parser("auto-capture", help="Capture recent errors from logs")
    
    # extract-patterns
    sub.add_parser("extract-patterns", help="Extract patterns from learnings into patterns.json")
    
    args = parser.parse_args()
    
    if args.cmd == "log-error":
        cmd_log_error(args)
    elif args.cmd == "log-learning":
        cmd_log_learning(args)
    elif args.cmd == "verify":
        print(cmd_verify(args))
    elif args.cmd == "report":
        print(cmd_report(args))
    elif args.cmd == "stats":
        print(cmd_stats(args))
    elif args.cmd == "auto-capture":
        print(capture_recent_errors())
    elif args.cmd == "extract-patterns":
        print(extract_patterns())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()


__all__ = ['generate_id', 'ensure_learnings_dir', 'append_entry', 'count_pending', 'build_error_entry', 'build_learning_entry', 'get_recent_errors', 'resolve_entry', 'auto_resolve_simple', 'promote_high_value_learning', 'capture_recent_errors', 'cmd_log_error', 'cmd_log_learning', 'cmd_verify', 'cmd_report', 'cmd_stats', 'extract_patterns', 'main']
