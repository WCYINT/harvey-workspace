#!/usr/bin/env python3
"""
Harvey 每5分钟快速检查（Python版，替代agent-based cron job）
避免嵌入式agent的READ-NO-PATH错误和超时重试风暴

执行：
1. 检查 health_check.log 健康状态
2. 检查 ERRORS.md 是否有新错误
3. 检查 evolution.log 进化引擎状态
4. 如有异常，写入日志
"""

import os
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

LOG_DIR = Path("/Users/fhjtech/.openclaw/logs")
ERRORS_FILE = Path("/Users/fhjtech/.openclaw/workspace/.learnings/ERRORS.md")
EVOLUTION_FILE = Path("/Users/fhjtech/.openclaw/workspace/.learnings/evolution.log")
HEALTH_FILE = LOG_DIR / "health_check.log"
LOG_OUT = LOG_DIR / "quarterly_review.log"
TZ_CST = timezone(timedelta(hours=8))

def log(msg: str) -> None:
    ts = datetime.now(TZ_CST).strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_OUT, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def read_last_lines(path: Path, n: int = 30) -> list:
    """Read last n lines of a file safely."""
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return lines[-n:]
    except Exception as e:
        return [f"Error reading: {e}"]

def main() -> None:
    issues = []
    
    # 1. Check health_check.log
    if HEALTH_FILE.exists():
        last_lines = read_last_lines(HEALTH_FILE, 10)
        last_content = "".join(last_lines)
        # Check for error patterns
        if "ERROR" in last_content or "FAIL" in last_content:
            issues.append(f"health_check.log: Errors detected in recent checks")
        # Check freshness (should have recent entries)
        try:
            # read_last_lines returns lines[-n:], so [0]=oldest of window, [-1]=newest
            last_line = last_lines[-1] if last_lines else ""
            if last_line:
                # Parse timestamp like [2026-04-04 19:20:00]
                ts_str = last_line[1:20] if last_line.startswith("[") else ""
                if ts_str:
                    last_ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                    age = (datetime.now(TZ_CST) - last_ts.replace(tzinfo=TZ_CST)).total_seconds()
                    if age > 900:  # 15 minutes old
                        issues.append(f"health_check.log stale: {age/60:.0f}min old")
        except Exception:
            pass
    else:
        issues.append("health_check.log: File not found")
    
    # 2. Check ERRORS.md for unresolved entries
    if ERRORS_FILE.exists():
        last_lines = read_last_lines(ERRORS_FILE, 50)
        last_content = "".join(last_lines)
        # Count in_progress errors
        in_progress_count = last_content.count("Status**: in_progress")
        pending_count = last_content.count("Status**: pending")
        if in_progress_count > 3:
            issues.append(f"ERRORS.md: {in_progress_count} in_progress errors")
        if pending_count > 0:
            issues.append(f"ERRORS.md: {pending_count} pending errors")
    else:
        issues.append("ERRORS.md: File not found")
    
    # 3. Check evolution.log
    if EVOLUTION_FILE.exists():
        last_lines = read_last_lines(EVOLUTION_FILE, 10)
        last_content = "".join(last_lines)
        if "ERROR" in last_content or "FAIL" in last_content:
            issues.append("evolution.log: Errors detected")
    else:
        issues.append("evolution.log: File not found")
    
    if issues:
        for issue in issues:
            log(f"ISSUE: {issue}")
    else:
        log("OK: All checks passed")

if __name__ == "__main__":
    main()


__all__ = ['log', 'read_last_lines', 'main']
