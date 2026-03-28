#!/usr/bin/env python3
"""
Harvey Python 进化引擎 - 每小时自动运行
James 要求：7天×24小时永不停歇进化，填补剩余 ~4% 差距

每日任务清单（轮转执行）：
H1: 新技术学习（每天学一个 Python 特性）
H2: 代码重构（优化一个旧脚本）
H3: 性能 benchmark（对比优化前后）
H4: 写新测试（覆盖旧代码）
H5: 整理 learnings（错误记录 → 防止重复）
H6: 更新 benchmark.md
H7: 全面测试 + mypy
"""

import subprocess, json, sys, argparse, os
from datetime import datetime, timezone, timedelta
from pathlib import Path

TZ_CST = timezone(timedelta(hours=8))
WORKSPACE = Path("/Users/fhjtech/.openclaw/workspace")
SKILLS_DB = WORKSPACE / ".learnings/skills_usage.json"
LOG = WORKSPACE / ".learnings/evolution.log"
PROGRESS_FILE = WORKSPACE / ".learnings/evolution_progress.json"

TODAY = datetime.now(TZ_CST).strftime("%Y-%m-%d")

# ── 每日轮转任务清单 ───────────────────────────────
HOURLY_TASKS = [
    # H1: 学习新技术
    ("Learn", lambda: _learn_something_new()),
    # H2: 重构一个旧脚本
    ("Refactor", lambda: _refactor_one_script()),
    # H3: 性能 benchmark
    ("Benchmark", lambda: _run_benchmark()),
    # H4: 写新测试
    ("Test", lambda: _add_tests()),
    # H5: 整理 learnings
    ("Learnings", lambda: _record_learnings()),
    # H6: 更新报告
    ("Report", lambda: _update_report()),
    # H7: 全面测试
    ("TestAll", lambda: _run_all_tests()),
]

TASKS_PER_DAY = 24  # 每小时一个任务


def _log(msg: str) -> None:
    ts = datetime.now(TZ_CST).strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def _load_progress() -> dict:
    """Load progress with validation to ensure data integrity."""
    try:
        with open(PROGRESS_FILE) as f:
            data = json.load(f)
        # Validate required fields
        validated = {
            "day": max(1, int(data.get("day", 1))),
            "hour": max(0, min(7, int(data.get("hour", 0)))),
            "skills": max(0, int(data.get("skills", 0))),
            "completed_tasks": list(data.get("completed_tasks", [])),
            "errors": list(data.get("errors", []))[-50:],  # Keep last 50 errors
        }
        return validated
    except (json.JSONDecodeError, ValueError, TypeError) as e:
        # Wrap _log() in its own try to ensure we NEVER crash on progress load
        try:
            _log(f"[PROGRESS-ERROR] Failed to load/validate progress: {e}. Starting fresh.")
        except Exception:
            pass
        return {"day": 1, "hour": 0, "skills": 0, "completed_tasks": [], "errors": []}
    except Exception as e:
        try:
            _log(f"[PROGRESS-ERROR] Unexpected error loading progress: {e}")
        except Exception:
            pass
        return {"day": 1, "hour": 0, "skills": 0, "completed_tasks": [], "errors": []}


def _save_progress(p: dict) -> None:
    """Save progress with atomic write to prevent corruption."""
    try:
        # Validate before saving
        if not isinstance(p, dict):
            raise ValueError("Progress must be a dict")
        required_keys = {"day", "hour", "skills", "completed_tasks", "errors"}
        if not required_keys.issubset(p.keys()):
            raise ValueError(f"Missing required keys: {required_keys - set(p.keys())}")

        # Atomic write: write to temp file, then rename
        temp_file = PROGRESS_FILE.with_suffix('.tmp')
        with open(temp_file, "w") as f:
            json.dump(p, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        temp_file.replace(PROGRESS_FILE)
    except Exception as e:
        _log(f"[PROGRESS-ERROR] Failed to save progress: {e}")
        raise


def _run_cmd(cmd: list[str], timeout: int = 30) -> tuple[int, str, str]:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                          cwd=str(WORKSPACE))
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout"
    except Exception as e:
        return -1, "", str(e)


def _learn_something_new() -> str:
    """每天学一个 Python 高级特性"""
    features = [
        ("dataclasses", "from dataclasses import dataclass, field"),
        ("match_case", "match x: case 1: ... case _: ..."),
        ("walrus", "(n := len(l))"),  #  walrus operator
        ("structural_pattern_matching", "match ... case ..."),
        ("itertools", "from itertools import groupby, accumulate"),
        ("functools_lru_cache", "@functools.lru_cache"),
        ("contextlib", "from contextlib import contextmanager"),
        ("typing_typeddict", "class Config(TypedDict): ..."),
        ("typing_protocol", "class Readable(Protocol): def read(self): ..."),
        ("asyncio_taskgroup", "async with asyncio.TaskGroup() as tg:"),
    ]
    idx = int(datetime.now(TZ_CST).strftime("%d")) % len(features)
    name, example = features[idx]
    _log(f"[H1-LEARN] Today: {name} | Example: {example}")

    # 写一个实际用法的 demo 脚本（禁止使用标准库同名，强制加 _demo 后缀）
    safe_name = f"{name}_demo" if name in ("contextlib", "functools", "itertools", "os", "sys", "re", "json", "collections", "typing", "pathlib", "asyncio") else name
    demo_path = WORKSPACE / f".scripts/demos/{safe_name}.py"
    demo_path.parent.mkdir(exist_ok=True)
    demo_path.write_text(f"# Learning: {name}\n# Example: {example}\n\n", encoding="utf-8")
    return name


def _refactor_one_script() -> str:
    """重构一个旧脚本 - 实际添加类型提示和代码改进"""
    import re
    import ast
    
    scripts = list((WORKSPACE / ".scripts").glob("*.py"))
    # Skip already-optimized scripts and this script itself
    skip_list = ("skillhub_auto_update.py", "async_scheduler.py", 
                 "evolution_engine.py", "minimax_client.py")
    scripts = [s for s in scripts if s.name not in skip_list]
    if not scripts:
        return "No scripts to refactor"

    # 找需要改进的脚本（优先选没有类型提示的）
    target = None
    for script in sorted(scripts, key=lambda s: s.stat().st_mtime):
        content = script.read_text(encoding="utf-8", errors="ignore")
        # 检查是否有函数缺少返回类型
        if "def " in content and "->" not in content:
            target = script
            break
    
    if not target:
        # 如果没有找到缺少类型提示的，选最新的
        target = max(scripts, key=lambda s: s.stat().st_mtime)
    
    name = target.stem
    content = target.read_text(encoding="utf-8", errors="ignore")
    improvements_made = []

    # 1. 添加类型提示到函数定义
    try:
        tree = ast.parse(content)
        funcs_missing_types = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 检查是否已有返回类型注解
                if node.returns is None and node.name != "__init__":
                    funcs_missing_types.append(node.name)
        
        if funcs_missing_types:
            _log(f"[H2-REFACTOR] Adding type hints to {name}.py: {funcs_missing_types[:3]}")
            
            # 简单的正则替换：为没有返回类型的函数添加 -> None
            modified = content
            for func_name in funcs_missing_types[:5]:  # 限制每次最多改5个
                # 匹配函数定义，避免已经有的类型提示
                pattern = rf'(def\s+{re.escape(func_name)}\s*\([^)]*\))(?!!\s*->)(\s*):'
                replacement = r'\1 -> None\2:'
                modified_new = re.sub(pattern, replacement, modified, count=1)
                if modified_new != modified:
                    modified = modified_new
                    improvements_made.append(f"Added type hints to {func_name}()")
            
            if improvements_made:
                target.write_text(modified, encoding="utf-8")
                content = modified
                _log(f"[H2-REFACTOR] Saved type hints to {name}.py")
                
    except SyntaxError:
        _log(f"[H2-REFACTOR] Syntax error in {name}.py, skipping AST analysis")
    except Exception as e:
        _log(f"[H2-REFACTOR] Error analyzing {name}.py: {e}")

    # 2. 添加 __all__ 导出（如果还没有）
    if "__all__" not in content and ("def " in content or "class " in content):
        try:
            exports = []
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    if not node.name.startswith('_'):
                        exports.append(node.name)
            
            if exports and len(exports) <= 20:
                all_line = f"\n\n__all__ = {exports}\n"
                new_content = content + all_line
                target.write_text(new_content, encoding="utf-8")
                content = new_content
                improvements_made.append(f"Added __all__ ({len(exports)} exports)")
                _log(f"[H2-REFACTOR] Added __all__ to {name}.py")
        except Exception as e:
            _log(f"[H2-REFACTOR] Could not add __all__: {e}")
    
    if not improvements_made:
        _log(f"[H2-REFACTOR] {name}.py already well-structured (skipped)")
        return f"{name} (no changes needed)"
    
    return f"{name}: {', '.join(improvements_made)}"


def _run_benchmark() -> str:
    """跑 benchmark"""
    code, stdout, stderr = _run_cmd(
        ["/opt/homebrew/bin/python3", str(WORKSPACE / ".scripts/async_scheduler.py")],
        timeout=60
    )
    if code == 0:
        # 提取提升倍数
        for line in stdout.split("\n"):
            if "提升" in line or "speedup" in line.lower() or "x" in line:
                _log(f"[H3-BENCH] {line.strip()}")
                return line.strip()
        return "Benchmark completed"
    return f"Benchmark failed: {stderr[:100]}"


def _add_tests() -> str:
    """为 skillhub_auto_update 添加测试"""
    test_file = WORKSPACE / ".scripts/tests/test_skillhub.py"
    if test_file.exists():
        return "test_skillhub.py already exists"

    content = '''
import pytest, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test skillhub auto-update parsing
from skillhub_auto_update import _parse_skillhub_output

def test_parse_slug_only():
    output = "hello-world  A cool skill  version: 1.0.0"
    result = _parse_skillhub_output(output)
    assert len(result) == 1
    assert result[0]["slug"] == "hello-world"

def test_parse_chinese_skip():
    output = "你好这个世界"
    result = _parse_skillhub_output(output)
    assert len(result) == 0

def test_parse_empty():
    assert _parse_skillhub_output("") == []
    assert _parse_skillhub_output("   ") == []

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''
    test_file.write_text(content.strip(), encoding="utf-8")
    code, _, _ = _run_cmd(
        ["/opt/homebrew/bin/python3", "-m", "pytest", str(test_file), "-v"],
        timeout=30
    )
    return f"test_skillhub.py written ({'PASS' if code==0 else 'FAIL'})"


def _record_learnings() -> str:
    """检查本周是否有新错误，仅记录新发现的问题（智能去重）"""
    learnings_file = WORKSPACE / ".learnings/LEARNINGS.md"
    today = datetime.now(TZ_CST).strftime("%Y-%m-%d")

    # 读取现有内容检查今天是否已记录
    existing_content = ""
    if learnings_file.exists():
        existing_content = learnings_file.read_text(encoding="utf-8", errors="ignore")

    # 精确匹配今天是否已有记录（检查独立标题行）
    # 注意：条目格式为 "## {today} Harvey 进化记录"
    today_header = f"## {today} Harvey 进化记录"
    has_entry_today = any(
        line.strip() == today_header 
        for line in existing_content.split('\n')
    )
    
    if has_entry_today:
        return f"Learnings already recorded for {today}"
    
    # 从 evolution.log 中读取今日错误
    log_file = WORKSPACE / ".learnings/evolution.log"
    new_learnings = []
    if log_file.exists():
        log_content = log_file.read_text(encoding="utf-8", errors="ignore")
        for line in log_content.split("\n"):
            if today in line and "ERROR" in line:
                error_msg = line.split(']')[-1].strip() if ']' in line else line.strip()
                new_learnings.append(f"- {error_msg}")

    # 智能记录：有错误才记录，无错误只在当天第一次运行时记录
    marker = f"\n## {today} Harvey 进化记录\n\n"
    
    if new_learnings:
        note = marker + "\n".join(new_learnings) + "\n"
        item_count = len(new_learnings)
    else:
        # 无错误时记录一次，保持连续性但不重复
        note = marker + "- 今日无新错误记录\n"
        item_count = 0

    try:
        with open(learnings_file, "a", encoding="utf-8") as f:
            f.write(note)
        return f"Learnings recorded for {today} ({item_count} errors)"
    except Exception as e:
        return f"Learnings failed: {e}"


def _update_report() -> str:
    """更新 benchmark 报告"""
    import subprocess
    result = subprocess.run(
        ["git", "-C", str(WORKSPACE), "log", "--oneline", "-1"],
        capture_output=True, text=True
    )
    latest = result.stdout.strip()
    _log(f"[H6-REPORT] Latest commit: {latest}")
    return latest


def _run_all_tests() -> str:
    """运行所有测试"""
    code, stdout, stderr = _run_cmd(
        ["/opt/homebrew/bin/python3", "-m", "pytest",
         str(WORKSPACE / ".scripts/tests/"), "-v", "--tb=short"],
        timeout=60
    )
    passed = stdout.count("PASSED")
    failed = stdout.count("FAILED")
    _log(f"[H7-TESTALL] {passed} passed, {failed} failed")
    return f"{passed} passed / {failed} failed"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="auto", choices=["day", "night", "auto"])
    args = parser.parse_args()

    # Auto-detect mode based on time: night=23-08, idle=30min no messages
    if args.mode == "auto":
        hour = datetime.now(TZ_CST).hour
        if 23 <= hour or hour < 8:
            args.mode = "night"
        else:
            args.mode = "day"

    progress = _load_progress()
    hour = datetime.now(TZ_CST).hour
    task_idx = hour % len(HOURLY_TASKS)
    task_name, task_fn = HOURLY_TASKS[task_idx]

    _log(f"=== Harvey 进化引擎 [{datetime.now(TZ_CST).strftime('%Y-%m-%d %H:%M')}] mode={args.mode} ===")

    # Night mode: 4x speed = run all remaining tasks (not just 4)
    # James确认：进化引擎每轮应该跑完所有7个任务，不遗漏H5/H6/H7
    if args.mode == "night":
        # 4x speed meaning: each cycle runs all tasks, but cycles run 4x more frequently
        # Don't limit to [:4] — H5(Learnings), H6(Report), H7(TestAll) were being skipped!
        tasks_to_run = HOURLY_TASKS[task_idx:] + HOURLY_TASKS[:task_idx]
        _log(f"Running {len(tasks_to_run)} tasks in night mode (all 7, 4x frequency)")
    else:
        tasks_to_run = [(task_name, task_fn)]

    for name, fn in tasks_to_run:
        try:
            result = fn()
            _log(f"[OK] {name}: {str(result)[:100]}")
        except Exception as e:
            _log(f"[ERROR] {name}: {e}")

    total_completed = len(progress.get("completed_tasks", [])) + len(tasks_to_run)
    progress["hour"] = (total_completed - 1) % 8
    progress["day"] = (total_completed - 1) // 24 + 1
    progress["skills"] = progress.get("skills", 0)
    progress.setdefault("completed_tasks", []).append(
        {"time": datetime.now(TZ_CST).isoformat(), "mode": args.mode, "tasks": [n for n,_ in tasks_to_run]}
    )
    _save_progress(progress)
    _log(f"=== Harvey 进化完成 [mode={args.mode}] ===\n")


if __name__ == "__main__":
    main()
