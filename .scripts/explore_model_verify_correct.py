#!/usr/bin/env python3
"""
explore_model_verify_correct.py
Harvey 自我进化核心循环：探索-建模-验证-修正

灵感来源：
- ARC-AGI-3: 人类学习 = 假设驱动 + 在线修正
- Anthropic Claude OS: 工具自迭代 + 效率分类器

核心思想：
- 每次失败不是终点，而是探索的起点
- 构建世界模型 → 验证假设 → 修正模型 → 记录进化
"""

import json
import time
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

TZ = timezone(timedelta(hours=8))
LOG_DIR = Path.home() / ".openclaw/workspace/.learnings"
EMCV_LOG = LOG_DIR / "explore_model_verify_correct.jsonl"


def _ensure_log():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    if not EMCV_LOG.exists():
        EMCV_LOG.write_text("")


def log_exploration(
    event_type: str,  # "explore" | "model" | "verify" | "correct"
    hypothesis: str,
    action: str,
    result: str,
    feedback: str,
    efficiency_steps: Optional[int] = None,
    human_steps_baseline: Optional[int] = None,
    metadata: Optional[dict] = None,
):
    """
    记录一次完整的探索-建模-验证-修正循环。
    
    ARC-AGI-3 效率评分: (human_steps/ai_steps)^2
    如果没有人类基线，设为 None。
    """
    _ensure_log()
    
    entry = {
        "timestamp": datetime.now(TZ).isoformat(),
        "event_type": event_type,
        "hypothesis": hypothesis,
        "action": action,
        "result": result,
        "feedback": feedback,
        "efficiency_steps": efficiency_steps,
        "human_steps_baseline": human_steps_baseline,
        "efficiency_score": None,
    }
    
    if efficiency_steps and human_steps_baseline and human_steps_baseline > 0:
        entry["efficiency_score"] = (human_steps_baseline / efficiency_steps) ** 2
    
    if metadata:
        entry["metadata"] = metadata
    
    with open(EMCV_LOG, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    return entry


def get_recent_logs(limit: int = 20) -> list:
    """获取最近的探索日志"""
    _ensure_log()
    logs = []
    with open(EMCV_LOG) as f:
        lines = f.readlines()
    for line in reversed(lines[-limit:]):
        try:
            logs.append(json.loads(line))
        except:
            pass
    return list(reversed(logs))


def analyze_hypothesis_stuckness(hypothesis: str, lookback: int = 10) -> dict:
    """
    检测某个假设是否长期无正反馈（死磕问题）。
    参考 ARC-AGI-3 发现：AI 会死磕错误假设到底。
    """
    _ensure_log()
    logs = get_recent_logs(lookback * 2)
    
    matching = [l for l in logs if l.get("hypothesis") == hypothesis]
    if not matching:
        return {"stuck": False, "reason": "no_matching_hypothesis"}
    
    # 检查最近N次是否有正反馈
    positive = [l for l in matching[-lookback:] if "success" in l.get("result", "").lower() or "✅" in l.get("feedback", "")]
    
    stuck = len(positive) == 0 and len(matching) >= 3
    return {
        "stuck": stuck,
        "hypothesis": hypothesis,
        "attempts": len(matching),
        "positive_count": len(positive),
        "advice": "建议修正假设，重新探索" if stuck else "假设运行正常",
    }


def get_efficiency_report() -> dict:
    """生成效率评分报告，参考 ARC-AGI-3 评分方式"""
    logs = get_recent_logs(100)
    
    scored = [l for l in logs if l.get("efficiency_score") is not None]
    if not scored:
        return {"message": "暂无有效评分数据", "count": 0}
    
    scores = [l["efficiency_score"] for l in scored]
    return {
        "count": len(scores),
        "avg_efficiency": sum(scores) / len(scores),
        "max_efficiency": max(scores),
        "min_efficiency": min(scores),
        "scores_below_1pct": len([s for s in scores if s < 0.01]),
        "recent": scored[-5:],
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Harvey 探索-建模-验证-修正日志")
    sub = parser.add_subparsers(dest="cmd")
    
    p_stats = sub.add_parser("stats", help="查看效率统计")
    p_recent = sub.add_parser("recent", help="查看最近日志")
    p_analyze = sub.add_parser("analyze", help="分析假设是否死磕")
    p_analyze.add_argument("--hypothesis", help="假设内容（用于死磕检测）")
    p_log = sub.add_parser("log", help="记录新探索")
    p_log.add_argument("hypothesis", help="假设内容")
    p_log.add_argument("action", help="采取的行动")
    p_log.add_argument("result", help="执行结果")
    p_log.add_argument("feedback", help="环境反馈")
    p_log.add_argument("ai_steps", type=int, help="AI尝试步数")
    p_log.add_argument("human_steps", type=int, help="人类基准步数")
    
    args = parser.parse_args()
    
    if args.cmd == "stats":
        report = get_efficiency_report()
        print(json.dumps(report, indent=2, ensure_ascii=False))
    elif args.cmd == "recent":
        for log in get_recent_logs():
            print(json.dumps(log, ensure_ascii=False))
    elif args.cmd == "analyze":
        if not args.hypothesis:
            print("需要 --hypothesis")
        else:
            result = analyze_hypothesis_stuckness(args.hypothesis)
            print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.cmd == "log":
        h, a, r, f = args.hypothesis, args.action, args.result, args.feedback
        ai_s, hu_s = args.ai_steps, args.human_steps
        entry = log_exploration(
            event_type="correct",
            hypothesis=h,
            action=a,
            result=r,
            feedback=f,
            efficiency_steps=int(ai_s),
            human_steps_baseline=int(hu_s),
        )
        print(f"✅ 记录: efficiency_score={entry['efficiency_score']}")
    else:
        parser.print_help()
