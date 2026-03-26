#!/usr/bin/env python3
"""
prm_self_review.py — Harvey PRM (Process Reward Model) Self-Review System

Implements AIBuildAI-inspired三层架构 for Harvey:
  PRM: 步骤级精准推理 — 执行前自我质疑每一步是否合理
  ORM: 结果级校验 — 执行后验证结果是否符合预期

Usage:
    python3 prm_self_review.py --plan "complex task description"
    python3 prm_self_review.py --validate --task-id TASK-20260326-001
    python3 prm_self_review.py --review-log --limit 10
"""

import os
import sys
import json
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

WORKSPACE = Path.home() / ".openclaw" / "workspace"
LEARNINGS_DIR = WORKSPACE / ".learnings"
LOGS_DIR = Path.home() / ".openclaw" / "logs"
PLANS_DIR = WORKSPACE / ".prm_plans"
PLANS_DIR.mkdir(exist_ok=True)

# ─── Task complexity classification ──────────────────────────────────────────

COMPLEXITY_THRESHOLDS = {
    "HIGH": [
        "写", "修改", "删除", "创建", "commit", "push",
        "发送", "邮件", "飞书", "通知",
        "重写", "重构", "更新多个", "批量",
        "安装", "uninstall", "删除",
        "sql", "database", "DROP", "CREATE TABLE",
        "权限", "chmod", "chown", "sudo",
        "cron", "launchd", "systemctl",
        "退休", "开除", "delete", "remove",
    ],
    "MEDIUM": [
        "优化", "改进", "分析", "检查", "审查",
        "比较", "评估", "研究", "查找",
        "多个文件", "跨文件", "refactor",
        "配置文件", "config", "settings",
        "自动化", "auto", "script",
        "测试", "test", "验证",
    ],
    "LOW": [
        "读取", "查看", "显示", "列出", "ls", "cat", "head",
        "状态", "status", "统计", "stats",
        "搜索", "grep", "find", "search",
        "问", "？", "?",
    ]
}


def classify_complexity(task: str) -> str:
    """Classify task complexity based on keyword matching."""
    task_lower = task.lower()
    high_score = sum(1 for kw in COMPLEXITY_THRESHOLDS["HIGH"] if kw in task_lower)
    med_score = sum(1 for kw in COMPLEXITY_THRESHOLDS["MEDIUM"] if kw in task_lower)
    
    if high_score >= 1:
        return "HIGH"
    elif med_score >= 2:
        return "MEDIUM"
    else:
        return "LOW"


def should_require_plan(task: str) -> bool:
    """Decide whether to require a formal plan + James confirmation."""
    return classify_complexity(task) in ("HIGH", "MEDIUM")


# ─── PRM: Step-level reasoning ────────────────────────────────────────────────

def generate_steps(task: str, complexity: str) -> list:
    """Generate execution steps for a task using heuristic decomposition."""
    steps = []
    task_lower = task.lower()
    
    # File operations
    if any(kw in task_lower for kw in ["修改", "写", "编辑", "更新", "重写"]):
        if "论文" in task or "mba" in task_lower or "chapter" in task_lower:
            steps.extend([
                {"step": 1, "action": "READ", "target": "读取论文相关章节内容", "risk": "LOW"},
                {"step": 2, "action": "ANALYZE", "target": "分析当前内容的逻辑结构", "risk": "LOW"},
                {"step": 3, "action": "PLAN", "target": "提出3个修改方案（含优缺点）", "risk": "LOW"},
                {"step": 4, "action": "WAIT_CONFIRM", "target": "等待James确认方案", "risk": "HIGH", "note": "阻塞等待"},
                {"step": 5, "action": "EXECUTE", "target": "执行选定方案", "risk": "MEDIUM"},
                {"step": 6, "action": "VERIFY", "target": "验证修改结果", "risk": "LOW"},
            ])
        else:
            steps.extend([
                {"step": 1, "action": "READ", "target": "读取目标文件当前内容", "risk": "LOW"},
                {"step": 2, "action": "ANALYZE", "target": "理解修改需求和影响范围", "risk": "LOW"},
                {"step": 3, "action": "PLAN", "target": "制定修改方案", "risk": "LOW"},
                {"step": 4, "action": "WAIT_CONFIRM", "target": "等待James确认", "risk": "HIGH"},
                {"step": 5, "action": "EXECUTE", "target": "执行修改", "risk": "MEDIUM"},
                {"step": 6, "action": "VERIFY", "target": "验证修改", "risk": "LOW"},
            ])
    
    # External communication
    elif any(kw in task_lower for kw in ["发送", "邮件", "飞书", "通知", "发送邮件"]):
        steps.extend([
            {"step": 1, "action": "DRAFT", "target": "起草消息内容", "risk": "LOW"},
            {"step": 2, "action": "CHECK_RECIPIENT", "target": "确认收件人地址/ID正确", "risk": "HIGH", "note": "发错人无法撤回"},
            {"step": 3, "action": "INCLUDE_PLAN", "target": "确保包含下一步计划和执行理由", "risk": "MEDIUM"},
            {"step": 4, "action": "WAIT_CONFIRM", "target": "等待James确认发送", "risk": "HIGH"},
            {"step": 5, "action": "SEND", "target": "发送消息", "risk": "HIGH"},
            {"step": 6, "action": "LOG", "target": "记录发送结果到日志", "risk": "LOW"},
        ])
    
    # System/code changes
    elif any(kw in task_lower for kw in ["安装", "删除", "cron", "launchd", "config", "重构"]):
        steps.extend([
            {"step": 1, "action": "CHECK_ENV", "target": "检查当前环境状态", "risk": "LOW"},
            {"step": 2, "action": "READ_PATTERNS", "target": "查询patterns.json是否有相关预防规则", "risk": "LOW"},
            {"step": 3, "action": "PLAN", "target": "制定执行计划（含回滚方案）", "risk": "MEDIUM"},
            {"step": 4, "action": "WAIT_CONFIRM", "target": "等待James确认", "risk": "HIGH"},
            {"step": 5, "action": "BACKUP", "target": "备份当前状态", "risk": "LOW"},
            {"step": 6, "action": "EXECUTE", "target": "执行变更", "risk": "HIGH"},
            {"step": 7, "action": "VERIFY", "target": "验证变更结果", "risk": "MEDIUM"},
        ])
    
    # Research/analysis tasks
    elif any(kw in task_lower for kw in ["研究", "分析", "查找", "调研", "分析", "比较"]):
        steps.extend([
            {"step": 1, "action": "DEFINE_SCOPE", "target": "明确研究范围和目标", "risk": "LOW"},
            {"step": 2, "action": "SEARCH", "target": "搜集相关信息", "risk": "LOW"},
            {"step": 3, "action": "ANALYZE", "target": "分析整理发现", "risk": "LOW"},
            {"step": 4, "action": "PRESENT_OPTIONS", "target": "提出3个方案（含数据支撑）", "risk": "LOW"},
            {"step": 5, "action": "WAIT_CONFIRM", "target": "等待James确认方向", "risk": "HIGH"},
            {"step": 6, "action": "DEEP_DIVE", "target": "深入执行选定方向", "risk": "LOW"},
        ])
    
    # Default simple path
    else:
        steps.extend([
            {"step": 1, "action": "EXECUTE", "target": f"执行: {task[:50]}", "risk": "LOW"},
            {"step": 2, "action": "VERIFY", "target": "验证结果", "risk": "LOW"},
        ])
    
    return steps


def prm_self_check(steps: list) -> dict:
    """
    PRM: 步骤级精准推理 — 检查每一步的风险和合理性.
    Returns dict with issues found and overall assessment.
    """
    issues = []
    risk_scores = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
    
    # Check for missing WAIT_CONFIRM in high-risk tasks
    high_risk_steps = [s for s in steps if s.get("risk") == "HIGH"]
    if high_risk_steps:
        has_confirm = any(s["action"] == "WAIT_CONFIRM" for s in steps)
        if not has_confirm:
            issues.append({
                "type": "MISSING_CONFIRM",
                "severity": "HIGH",
                "message": "高风险任务缺少 WAIT_CONFIRM 步骤，需要 James 确认后才能继续"
            })
    
    # Check step ordering
    step_nums = [s["step"] for s in steps]
    if step_nums != sorted(step_nums):
        issues.append({
            "type": "WRONG_ORDER",
            "severity": "MEDIUM",
            "message": "步骤编号不连续，请检查执行顺序"
        })
    
    # Check for missing VERIFY step
    actions = [s["action"] for s in steps]
    has_verify = "VERIFY" in actions or "CHECK" in actions
    if not has_verify and len(steps) > 1:
        issues.append({
            "type": "MISSING_VERIFY",
            "severity": "LOW",
            "message": "建议添加 VERIFY 步骤以验证执行结果"
        })
    
    # Check for back-up in system changes (only WRITE operations need backup)
    write_actions = ["DELETE", "DROP", "PUSH", "WRITE", "OVERWRITE", "TRUNCATE"]
    has_write = any(a in actions for a in write_actions)
    has_read = "READ" in actions or "CHECK" in actions
    if has_write and not has_read:
        issues.append({
            "type": "MISSING_BACKUP",
            "severity": "MEDIUM",
            "message": "写入操作建议先 BACKUP 当前状态"
        })
    
    # Calculate overall risk score
    total_risk = sum(risk_scores.get(s.get("risk", "LOW"), 0) for s in steps)
    overall = "LOW" if total_risk <= 2 else "MEDIUM" if total_risk <= 5 else "HIGH"
    
    return {
        "issues": issues,
        "overall_risk": overall,
        "total_steps": len(steps),
        "high_risk_count": len(high_risk_steps),
        "pass": len([i for i in issues if i["severity"] == "HIGH"]) == 0
    }


def orm_validate_outcome(task: str, outcome: str, plan_id: str) -> dict:
    """
    ORM: 结果级校验 — 验证执行结果是否符合预期.
    For use after plan execution to validate outcomes.
    """
    issues = []
    
    # Check if outcome is empty or too short
    if not outcome or len(outcome.strip()) < 10:
        issues.append({
            "type": "EMPTY_OUTCOME",
            "severity": "HIGH",
            "message": "执行结果为空或过短，可能执行失败"
        })
    
    # Check for common error patterns in outcome
    error_patterns = [
        ("error", "ERROR", "Error", "错误"),
        ("failed", "Failed", "FAIL"),
        ("exception", "Exception"),
        ("traceback", "Traceback"),
    ]
    for pattern, *_ in error_patterns:
        if pattern in outcome:
            issues.append({
                "type": "ERROR_IN_OUTCOME",
                "severity": "HIGH",
                "message": f"执行结果中发现错误模式: {pattern}"
            })
            break
    
    return {
        "issues": issues,
        "pass": len(issues) == 0,
        "validated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    }


# ─── Plan lifecycle ─────────────────────────────────────────────────────────

def create_plan(task: str, session_id: str = "") -> dict:
    """Create a new PRM plan for a task."""
    plan_id = f"TASK-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    complexity = classify_complexity(task)
    steps = generate_steps(task, complexity)
    prm_result = prm_self_check(steps)
    
    plan = {
        "plan_id": plan_id,
        "task": task,
        "complexity": complexity,
        "session_id": session_id,
        "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "status": "PENDING_CONFIRM" if should_require_plan(task) else "AUTO_APPROVED",
        "steps": steps,
        "prm_result": {
            "issues": prm_result["issues"],
            "overall_risk": prm_result["overall_risk"],
            "total_steps": prm_result["total_steps"],
            "high_risk_count": prm_result["high_risk_count"],
            "pass": prm_result["pass"],
        },
        "orm_results": [],
        "execution_log": [],
    }
    
    # Save plan
    plan_file = PLANS_DIR / f"{plan_id}.json"
    plan_file.write_text(json.dumps(plan, ensure_ascii=False, indent=2))
    
    return plan


def load_plan(plan_id: str) -> Optional[dict]:
    """Load an existing plan by ID."""
    plan_file = PLANS_DIR / f"{plan_id}.json"
    if not plan_file.exists():
        return None
    return json.loads(plan_file.read_text())


def approve_plan(plan_id: str, confirmed_step: int = None) -> dict:
    """Approve a plan (optionally at a specific step)."""
    plan = load_plan(plan_id)
    if not plan:
        return {"error": f"Plan {plan_id} not found"}
    
    plan["status"] = "APPROVED"
    plan["approved_at"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    plan["confirmed_step"] = confirmed_step
    
    plan_file = PLANS_DIR / f"{plan_id}.json"
    plan_file.write_text(json.dumps(plan, ensure_ascii=False, indent=2))
    
    return plan


def reject_plan(plan_id: str, reason: str = "") -> dict:
    """Reject a plan."""
    plan = load_plan(plan_id)
    if not plan:
        return {"error": f"Plan {plan_id} not found"}
    
    plan["status"] = "REJECTED"
    plan["rejected_at"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    plan["rejection_reason"] = reason
    
    plan_file = PLANS_DIR / f"{plan_id}.json"
    plan_file.write_text(json.dumps(plan, ensure_ascii=False, indent=2))
    
    return plan


def log_execution(plan_id: str, step: int, action: str, result: str):
    """Log execution of a step."""
    plan = load_plan(plan_id)
    if not plan:
        return
    
    plan["execution_log"].append({
        "step": step,
        "action": action,
        "result": result,
        "at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    })
    
    plan_file = PLANS_DIR / f"{plan_id}.json"
    plan_file.write_text(json.dumps(plan, ensure_ascii=False, indent=2))


# ─── Plan formatter ─────────────────────────────────────────────────────────

def format_plan_for_review(plan: dict) -> str:
    """Format a plan as a human-readable review request."""
    prm = plan["prm_result"]
    risk_emoji = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🔴"}
    risk = prm["overall_risk"]
    
    lines = [
        f"📋 **PRM 自审计划** [{plan['plan_id']}]",
        "",
        f"**任务**: {plan['task']}",
        f"**复杂度**: {plan['complexity']} | **整体风险**: {risk_emoji[risk]} {risk}",
    ]
    high_issues = len([i for i in prm['issues'] if i['severity'] == 'HIGH'])
    prm_check = '✅ 通过' if prm['pass'] else f'⚠️  {high_issues} 项高风险问题'
    lines.append(f"**PRM 检查**: {prm_check}")
    lines.append("")
    lines.append("**执行步骤:**")
    
    for step in plan["steps"]:
        risk_e = risk_emoji.get(step.get("risk", "LOW"), "⚪")
        confirm_marker = " ⏸️ [待确认]" if step.get("action") == "WAIT_CONFIRM" else ""
        note = f" ({step.get('note', '')})" if step.get("note") else ""
        lines.append(f"  {step['step']}. {risk_e} **{step['action']}**: {step['target']}{confirm_marker}{note}")
    
    if prm["issues"]:
        lines.append("")
        lines.append("**⚠️ PRM 发现的问题:**")
        for issue in prm["issues"]:
            sev = issue["severity"]
            lines.append(f"  - [{sev}] {issue['message']}")
    
    lines.append("")
    if plan["status"] == "PENDING_CONFIRM":
        lines.append("**⏸️ 等待 James 确认后执行**")
        lines.append("")
        lines.append("回复 `confirm {plan_id}` 确认执行，")
        lines.append("回复 `reject {plan_id} [原因]` 拒绝，")
        lines.append("回复 `modify {plan_id} #步骤 [改法]` 修改特定步骤")
    elif plan["status"] == "AUTO_APPROVED":
        lines.append("**✅ 低风险任务，自动批准执行**")
    
    return "\n".join(lines)


# ─── CLI ────────────────────────────────────────────────────────────────────

def cmd_plan(args):
    """Create a new PRM plan."""
    plan = create_plan(args.task, args.session or "")
    print(format_plan_for_review(plan))
    return plan["plan_id"]


def cmd_validate(args):
    """Validate an existing plan's outcome (ORM)."""
    plan = load_plan(args.plan_id)
    if not plan:
        print(f"❌ Plan {args.plan_id} not found")
        return
    
    result = orm_validate_outcome(plan["task"], args.outcome or "", args.plan_id)
    if result["pass"]:
        print(f"✅ ORM 校验通过 (validated: {result['validated_at']})")
    else:
        print(f"⚠️ ORM 发现 {len(result['issues'])} 个问题:")
        for issue in result["issues"]:
            print(f"  - [{issue['severity']}] {issue['message']}")
    
    # Store ORM result
    if plan:
        plan["orm_results"].append(result)
        (PLANS_DIR / f"{args.plan_id}.json").write_text(
            json.dumps(plan, ensure_ascii=False, indent=2))
    
    return result


def cmd_review_log(args):
    """Show recent plan history."""
    plans = sorted(PLANS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    
    lines = ["📜 **PRM 计划历史**\n"]
    for p in plans[:args.limit]:
        try:
            d = json.loads(p.read_text())
            status_icon = {"PENDING_CONFIRM": "⏸️", "APPROVED": "✅", 
                          "REJECTED": "❌", "COMPLETED": "🏁", "AUTO_APPROVED": "⚡"}
            icon = status_icon.get(d["status"], "❓")
            lines.append(
                f"{icon} [{d['plan_id']}] {d['task'][:40]} "
                f"({d['complexity']}/{d['prm_result']['overall_risk']}) "
                f"- {d['created_at'][:10]}"
            )
        except Exception:
            pass
    
    print("\n".join(lines))


def cmd_status(args):
    """Show PRM system status."""
    plans = sorted(PLANS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    pending = sum(1 for p in plans if json.loads(p.read_text()).get("status") == "PENDING_CONFIRM")
    approved = sum(1 for p in plans if json.loads(p.read_text()).get("status") == "APPROVED")
    completed = sum(1 for p in plans if json.loads(p.read_text()).get("status") == "COMPLETED")
    
    patterns_file = LEARNINGS_DIR / "patterns.json"
    patterns_count = 0
    if patterns_file.exists():
        d = json.loads(patterns_file.read_text())
        patterns_count = len(d.get("patterns", {}))
    
    print(f"""# PRM 自审系统状态

## 系统概览
- 总计划数: {len(plans)}
- 待确认: {pending} | 已批准: {approved} | 已完成: {completed}

## patterns.json
- 决策原则: {patterns_count} 条

## 复杂度分类规则
- HIGH: 涉及写/修改/删除/发送/安装/cron 等不可逆操作
- MEDIUM: 涉及优化/分析/自动化/多文件 等需谨慎操作
- LOW: 读取/查看/搜索/简单查询

## PRM 自审检查项
1. 高风险任务是否包含 WAIT_CONFIRM 步骤
2. 步骤编号是否连续
3. 是否有 VERIFY 步骤
4. 系统变更是否先 BACKUP

## ORM 结果校验
校验执行结果是否为空或包含错误模式
""")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Harvey PRM Self-Review System")
    sub = parser.add_subparsers(dest="cmd")
    
    p_plan = sub.add_parser("plan", help="Create a PRM plan for a task")
    p_plan.add_argument("--task", required=True, help="Task description")
    p_plan.add_argument("--session", default="", help="Session ID")
    
    p_val = sub.add_parser("validate", help="ORM validate execution outcome")
    p_val.add_argument("--plan-id", required=True)
    p_val.add_argument("--outcome", default="")
    
    p_log = sub.add_parser("review-log", help="Show recent plans")
    p_log.add_argument("--limit", type=int, default=10)
    
    sub.add_parser("status", help="Show PRM system status")
    
    args = parser.parse_args()
    
    if args.cmd == "plan":
        cmd_plan(args)
    elif args.cmd == "validate":
        cmd_validate(args)
    elif args.cmd == "review-log":
        cmd_review_log(args)
    elif args.cmd == "status":
        cmd_status(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
