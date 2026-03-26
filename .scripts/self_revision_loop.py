#!/usr/bin/env python3
"""
self_revision_loop.py — AIBuildAI Self-Revision Loop Implementation

Implements the core AIBuildAI innovation:
  执行 → 评估结果 → 识别问题 → 重新执行 → 再评估
  最多 MAX_RETRIES 次 (default: 3)

Usage:
    python3 self_revision_loop.py --execute "task description"
    python3 self_revision_loop.py --simulate "task" --outcome "result"
    python3 self_revision_loop.py --diagnose "failure text"
"""

import os
import sys
import json
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable

WORKSPACE = Path.home() / ".openclaw" / "workspace"
LEARNINGS_DIR = WORKSPACE / ".learnings"
PATTERNS_FILE = LEARNINGS_DIR / "patterns.json"
MAX_RETRIES = 3


# ─── Pattern Matcher ─────────────────────────────────────────────────────────

def load_patterns() -> dict:
    """Load patterns.json if it exists."""
    if PATTERNS_FILE.exists():
        return json.loads(PATTERNS_FILE.read_text())
    return {"patterns": {}, "error_signatures": {}}


def match_patterns(error_text: str) -> list:
    """Match error text against patterns.json for known fixes."""
    patterns_data = load_patterns()
    matched = []
    error_lower = error_text.lower()
    
    # Check error signatures
    for sig_key, sig_data in patterns_data.get("error_signatures", {}).items():
        for pattern in sig_data.get("patterns", []):
            if pattern.lower() in error_lower or pattern in error_text:
                matched.append({
                    "signature": sig_key,
                    "pattern": pattern,
                    "auto_fix": sig_data.get("auto_fix", ""),
                    "summary": sig_data.get("summary", "")
                })
    
    # Also check decision principles for triggers
    for prin_key, prin_data in patterns_data.get("patterns", {}).items():
        triggers = prin_data.get("trigger", [])
        for trigger in triggers:
            if trigger.lower() in error_lower:
                matched.append({
                    "principle": prin_key,
                    "trigger": trigger,
                    "fix": prin_data.get("fix", ""),
                    "prevention": prin_data.get("prevention", "")
                })
    
    return matched


# ─── Failure Diagnoser ───────────────────────────────────────────────────────

def diagnose_failure(error_text: str, attempt: int) -> dict:
    """
    Diagnose WHY a task failed and suggest corrective action.
    Inspired by AIBuildAI's PRM step-level analysis.
    """
    matched = match_patterns(error_text)
    suggestions = []
    root_cause = "unknown"
    can_retry = True
    
    # Classify failure type
    error_lower = error_text.lower()
    
    if any(kw in error_lower for kw in ["permission denied", "eacces", "EROFS"]):
        root_cause = "PERMISSION_ERROR"
        suggestions.append("检查文件/目录权限，使用 chmod/chown 修复")
        suggestions.append("确认操作路径是否对当前用户可写")
        can_retry = True
        
    elif any(kw in error_lower for kw in ["not found", "enoent", "no such file", "does not exist", "不存在", "找不到", "无法找到"]):
        root_cause = "PATH_NOT_FOUND"
        suggestions.append("确认目标路径是否存在")
        suggestions.append("检查是否需要先创建父目录")
        suggestions.append("使用绝对路径而非相对路径")
        can_retry = True
        
    elif any(kw in error_lower for kw in ["timeout", "timed out", "deadline", "超时"]):
        root_cause = "TIMEOUT"
        suggestions.append("增加 timeout 参数")
        suggestions.append("简化操作步骤，分批执行")
        suggestions.append("检查网络连接是否稳定")
        can_retry = True
        
    elif any(kw in error_lower for kw in ["syntaxerror", "syntax error", "parse error", "语法错误"]):
        root_cause = "SYNTAX_ERROR"
        suggestions.append("检查代码语法错误")
        suggestions.append("确认 Python 版本兼容性")
        can_retry = True
        
    elif any(kw in error_lower for kw in ["importerror", "modulenotfound", "cannot find module", "导入错误", "模块未找到"]):
        root_cause = "IMPORT_ERROR"
        suggestions.append("确认模块已安装: pip install <module>")
        suggestions.append("检查 PYTHONPATH 环境变量")
        suggestions.append("确认 jiti 缓存已清理 (rm -rf /tmp/jiti/)")
        can_retry = True
        
    elif any(kw in error_lower for kw in ["535", "authentication failed", "smtp", "auth", "认证失败", "授权码"]):
        root_cause = "SMTP_AUTH_ERROR"
        suggestions.append("检查 SMTP 授权码是否过期")
        suggestions.append("参考 patterns.json: smtp-resilience")
        suggestions.append("更新 TOOLS.md 中的授权码")
        can_retry = False  # Can't retry until credential is fixed
        
    elif any(kw in error_lower for kw in ["duplicate", "already exists", "already logged", "重复", "已存在"]):
        root_cause = "DUPLICATE_ERROR"
        suggestions.append("检查是否已存在重复条目")
        suggestions.append("使用 exact-match 验证")
        can_retry = False
        
    elif any(kw in error_lower for kw in ["exit code", "command exited"]):
        exit_code = re.search(r"exit code (\d+)", error_text)
        code = exit_code.group(1) if exit_code else "?"
        root_cause = f"EXIT_CODE_{code}"
        suggestions.append(f"命令退出码 {code}，表示一般错误")
        if code == "1":
            suggestions.append("检查命令参数是否正确")
        elif code == "127":
            suggestions.append("命令不存在，检查 PATH")
        can_retry = True
        
    elif any(kw in error_lower for kw in ["keyboard interrupt", "sigterm", "sigint", "killed"]):
        root_cause = "INTERRUPTED"
        suggestions.append("进程被信号中断，可能是超时或内存不足")
        can_retry = True
        
    elif len(error_text.strip()) < 5 or not error_text:
        root_cause = "EMPTY_OUTPUT"
        suggestions.append("执行结果为空，可能命令未正常执行")
        suggestions.append("检查命令是否正确，尝试简化命令")
        can_retry = True
        
    else:
        root_cause = "UNKNOWN_ERROR"
        suggestions.append("无法自动识别错误类型")
        suggestions.append("查看完整错误信息后手动分析")
        # Check if there are pattern matches
        if matched:
            for m in matched[:2]:
                if "auto_fix" in m:
                    suggestions.append(f"patterns.json 参考: {m['auto_fix']}")
    
    return {
        "root_cause": root_cause,
        "attempt": attempt,
        "can_retry": can_retry,
        "suggestions": suggestions,
        "pattern_matches": matched[:3],
        "diagnosed_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    }


# ─── Self-Revision Loop ──────────────────────────────────────────────────────

class RevisionLoop:
    """
    AIBuildAI-style self-revision loop.
    
    Executes a task, validates result with ORM,
    and retries up to MAX_RETRIES if validation fails.
    """
    
    def __init__(self, task: str, executor: Callable[[], str]):
        self.task = task
        self.executor = executor  # Function that returns outcome string
        self.attempts = []
        self.final_outcome = None
        self.final_pass = None
        
    def run(self) -> dict:
        """Run the self-revision loop."""
        for attempt in range(1, MAX_RETRIES + 1):
            outcome = ""
            error = None
            
            try:
                outcome = self.executor()
            except Exception as e:
                error = str(e)
                outcome = f"Exception: {error}"
            
            # ORM validate outcome
            from prm_self_review import orm_validate_outcome
            orm_result = orm_validate_outcome(self.task, outcome, f"REVISION-{attempt}")
            
            # Record attempt
            self.attempts.append({
                "attempt": attempt,
                "outcome": outcome[:500] if len(outcome) > 500 else outcome,
                "orm_pass": orm_result["pass"],
                "orm_issues": orm_result["issues"],
            })
            
            if orm_result["pass"]:
                self.final_outcome = outcome
                self.final_pass = True
                return self._build_result()
            
            # ORM failed — diagnose and prepare retry
            diagnosis = diagnose_failure(outcome, attempt)
            self.attempts[-1]["diagnosis"] = diagnosis
            
            if not diagnosis["can_retry"] or attempt >= MAX_RETRIES:
                self.final_outcome = outcome
                self.final_pass = False
                return self._build_result()
            
            # Prepare adjusted attempt
            suggestions = diagnosis["suggestions"]
            self.attempts[-1]["retry_suggestions"] = suggestions
        
        return self._build_result()
    
    def _build_result(self) -> dict:
        attempts_made = len(self.attempts)
        passed = self.final_pass
        
        return {
            "task": self.task,
            "passed": passed,
            "attempts_made": attempts_made,
            "max_retries": MAX_RETRIES,
            "final_outcome": self.final_outcome[:500] if self.final_outcome and len(self.final_outcome) > 500 else self.final_outcome,
            "attempt_details": self.attempts,
            "conclusion": "✅ 通过" if passed else f"❌ 失败（{attempts_made}/{MAX_RETRIES} 次尝试）",
            "final_diagnosis": self.attempts[-1].get("diagnosis", {}) if self.attempts else {},
            "run_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
        }


# ─── CLI ────────────────────────────────────────────────────────────────────

def cmd_execute(args):
    """Execute a task with self-revision loop."""
    import prm_self_review
    
    def dummy_executor():
        # This is a demo — in real use, replace with actual task executor
        return args.simulate_outcome if args.simulate_outcome else "执行成功"
    
    loop = RevisionLoop(args.task, dummy_executor)
    result = loop.run()
    
    print(f"\n{'='*60}")
    print(f"📋 Self-Revision Loop 结果")
    print(f"{'='*60}")
    print(f"任务: {result['task']}")
    print(f"结论: {result['conclusion']}")
    print(f"尝试次数: {result['attempts_made']}/{result['max_retries']}")
    
    for att in result["attempt_details"]:
        status = "✅" if att.get("orm_pass") else "❌"
        print(f"\n  尝试 #{att['attempt']}: {status}")
        if att.get("diagnosis"):
            d = att["diagnosis"]
            print(f"    根因: {d['root_cause']}")
            print(f"    可重试: {d['can_retry']}")
            if d.get("suggestions"):
                print(f"    建议: {'; '.join(d['suggestions'][:2])}")
        if att.get("orm_issues"):
            for issue in att["orm_issues"]:
                print(f"    ORM 问题: [{issue['severity']}] {issue['message']}")
    
    if result.get("final_diagnosis"):
        print(f"\n最终诊断: {result['final_diagnosis'].get('root_cause', 'N/A')}")
    
    return result


def cmd_diagnose(args):
    """Diagnose a failure without executing."""
    result = diagnose_failure(args.error_text, attempt=1)
    
    print(f"\n🔍 诊断结果")
    print(f"{'='*50}")
    print(f"根因: {result['root_cause']}")
    print(f"可重试: {'是' if result['can_retry'] else '否'}")
    print(f"\n建议:")
    for i, s in enumerate(result["suggestions"], 1):
        print(f"  {i}. {s}")
    
    if result["pattern_matches"]:
        print(f"\n📌 patterns.json 匹配:")
        for m in result["pattern_matches"][:3]:
            if "auto_fix" in m:
                print(f"  - [{m['signature']}] {m['auto_fix']}")
            elif "principle" in m:
                print(f"  - [{m['principle']}] {m.get('prevention', m.get('fix', ''))[:100]}")
    
    return result


def cmd_simulate(args):
    """Simulate a self-revision loop with a given outcome."""
    # Simulate outcome → ORM validation → pass/fail
    from prm_self_review import orm_validate_outcome
    
    outcome = args.outcome
    plan_id = f"SIM-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    orm = orm_validate_outcome(args.task, outcome, plan_id)
    diagnosis = diagnose_failure(outcome if not orm["pass"] else "", 1)
    
    print(f"\n🔬 Self-Revision 模拟")
    print(f"{'='*50}")
    print(f"任务: {args.task}")
    print(f"结果: {outcome[:200]}")
    print(f"ORM 校验: {'✅ 通过' if orm['pass'] else '❌ 失败'}")
    
    if not orm["pass"]:
        print(f"\n诊断: {diagnosis['root_cause']}")
        print("建议:")
        for i, s in enumerate(diagnosis["suggestions"], 1):
            print(f"  {i}. {s}")
        print(f"\n是否重试: {'是' if diagnosis['can_retry'] else '否'}")
    
    return {"orm": orm, "diagnosis": diagnosis}


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Harvey Self-Revision Loop")
    sub = parser.add_subparsers(dest="cmd")
    
    p = sub.add_parser("execute", help="Execute task with self-revision loop")
    p.add_argument("--task", required=True)
    p.add_argument("--simulate-outcome", default="")
    
    p2 = sub.add_parser("diagnose", help="Diagnose a failure")
    p2.add_argument("--error-text", required=True)
    
    p3 = sub.add_parser("simulate", help="Simulate ORM + diagnosis for given outcome")
    p3.add_argument("--task", required=True)
    p3.add_argument("--outcome", required=True)
    
    args = parser.parse_args()
    
    if args.cmd == "execute":
        cmd_execute(args)
    elif args.cmd == "diagnose":
        cmd_diagnose(args)
    elif args.cmd == "simulate":
        cmd_simulate(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
