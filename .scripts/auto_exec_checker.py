#!/usr/bin/env python3
"""
1小时无回复自动执行检查器
检查最后发送的消息是否在1小时内收到回复，如无则自动执行默认操作
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# 配置
WORKSPACE = "/Users/fhjtech/.openclaw/workspace"
STATE_FILE = os.path.join(WORKSPACE, "email_integration", ".feishu_reminder_state.json")
MEMORY_DIR = os.path.join(WORKSPACE, "memory")
LOG_FILE = os.path.join(WORKSPACE, ".logs", "auto_exec.log")

# 时间配置
AUTO_EXEC_THRESHOLD_MINUTES = 60  # 1小时

# 确保日志目录存在
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def log(message) -> None:
    """记录日志"""
    ts = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{ts}] {message}"
    print(log_message)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_message + "\n")

def load_state() -> dict:
    """加载提醒状态"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            log(f"[ERROR] 加载状态文件失败: {e}")
    return {}

def check_auto_exec_condition(state) -> tuple[bool, str]:
    """
    检查是否满足自动执行条件
    返回: (should_exec: bool, reason: str)
    """
    # 检查是否有最后发送的消息
    last_msg_time = state.get("last_bot_msg_time")
    reminder_sent = state.get("reminder_sent", False)

    if not last_msg_time:
        return False, "没有记录到最后发送的消息"

    # 计算时间差
    now = datetime.now(timezone.utc)
    last_msg_dt = datetime.fromtimestamp(last_msg_time, tz=timezone.utc)
    time_diff_minutes = (now - last_msg_dt).total_seconds() / 60

    log(f"最后消息时间: {last_msg_dt.strftime('%H:%M:%S')}, "
        f"当前时间: {now.strftime('%H:%M:%S')}, "
        f"时间差: {time_diff_minutes:.1f}分钟")

    # 检查是否已经超过1小时
    if time_diff_minutes < AUTO_EXEC_THRESHOLD_MINUTES:
        remaining = AUTO_EXEC_THRESHOLD_MINUTES - time_diff_minutes
        return False, f"距离1小时还有 {remaining:.1f} 分钟"

    # 检查是否已经提醒过且用户未回复
    if reminder_sent:
        # 如果已经发送过提醒，且超过1小时，执行自动执行
        return True, f"已发送提醒且超过1小时 ({time_diff_minutes:.1f}分钟)，满足自动执行条件"

    # 如果没有发送过提醒，但已经超过1小时，也可以执行（根据业务规则）
    return True, f"超过1小时 ({time_diff_minutes:.1f}分钟)，满足自动执行条件"

def execute_default_action(state: dict) -> bool:
    """
    执行默认自动操作。
    从 state 中读取 default_action_type 和 default_action_payload，执行对应操作。
    """
    log("[ACTION] 开始执行默认自动操作...")

    # 从 state 中读取待执行动作
    action_type = state.get("default_action_type")
    action_payload = state.get("default_action_payload")

    exec_log_file = os.path.join(WORKSPACE, ".logs", "auto_exec_history.jsonl")
    os.makedirs(os.path.dirname(exec_log_file), exist_ok=True)

    if not action_type:
        log("[WARN] state 中未配置 default_action_type，无实际动作可执行")
        execution_record = {
            "timestamp": datetime.now(timezone(timedelta(hours=8))).isoformat(),
            "action": "none",
            "reason": "missing default_action_type in state",
            "trigger": "1_hour_no_reply",
            "status": "skipped"
        }
        with open(exec_log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(execution_record, ensure_ascii=False) + "\n")
        return True

    if action_type == "send_email":
        # payload: {"to": "...", "subject": "...", "body": "..."}
        to_addr = action_payload.get("to") if isinstance(action_payload, dict) else None
        subject = action_payload.get("subject", "(无主题)") if isinstance(action_payload, dict) else "(无主题)"
        body = action_payload.get("body", "") if isinstance(action_payload, dict) else str(action_payload)
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            auth_code = os.environ.get("HARVEY_EMAIL_AUTH", "xxx")
            msg = MIMEMultipart()
            msg["From"] = "wcyint@163.com"
            msg["To"] = to_addr or "wcyint@163.com"
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain", "utf-8"))
            with smtplib.SMTP_SSL("smtp.163.com", 465) as server:
                server.login("wcyint@163.com", auth_code)
                server.send_message(msg)
            execution_record = {
                "timestamp": datetime.now(timezone(timedelta(hours=8))).isoformat(),
                "action": "send_email",
                "to": to_addr,
                "subject": subject,
                "trigger": "1_hour_no_reply",
                "status": "sent"
            }
            log(f"[ACTION] 邮件已发送至 {to_addr}: {subject}")
        except Exception as e:
            execution_record = {
                "timestamp": datetime.now(timezone(timedelta(hours=8))).isoformat(),
                "action": "send_email",
                "error": str(e),
                "trigger": "1_hour_no_reply",
                "status": "failed"
            }
            log(f"[ERROR] 邮件发送失败: {e}")

    elif action_type == "run_script":
        script_path = action_payload.get("path") if isinstance(action_payload, dict) else action_payload
        if not script_path:
            log("[WARN] run_script 动作缺少 script path")
            execution_record = {
                "timestamp": datetime.now(timezone(timedelta(hours=8))).isoformat(),
                "action": "run_script",
                "error": "missing script path",
                "trigger": "1_hour_no_reply",
                "status": "skipped"
            }
        else:
            try:
                result = subprocess.run(
                    ["python3", script_path],
                    capture_output=True, text=True, timeout=300
                )
                execution_record = {
                    "timestamp": datetime.now(timezone(timedelta(hours=8))).isoformat(),
                    "action": "run_script",
                    "script": script_path,
                    "returncode": result.returncode,
                    "stdout": result.stdout[:500],
                    "stderr": result.stderr[:500],
                    "trigger": "1_hour_no_reply",
                    "status": "completed"
                }
                log(f"[ACTION] 脚本执行完成: {script_path}, 返回码: {result.returncode}")
            except Exception as e:
                execution_record = {
                    "timestamp": datetime.now(timezone(timedelta(hours=8))).isoformat(),
                    "action": "run_script",
                    "script": script_path,
                    "error": str(e),
                    "trigger": "1_hour_no_reply",
                    "status": "failed"
                }
                log(f"[ERROR] 脚本执行失败: {script_path}, 错误: {e}")

    else:
        execution_record = {
            "timestamp": datetime.now(timezone(timedelta(hours=8))).isoformat(),
            "action": action_type,
            "payload": action_payload,
            "trigger": "1_hour_no_reply",
            "status": f"unknown_action_type:{action_type}"
        }
        log(f"[WARN] 未知动作类型: {action_type}")

    with open(exec_log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(execution_record, ensure_ascii=False) + "\n")

    log("[ACTION] 自动操作记录已保存")
    return True

def main() -> int:
    """主函数"""
    log("=" * 60)
    log("1小时无回复自动执行检查器启动")
    log("=" * 60)

    # 加载状态
    state = load_state()
    if not state:
        log("[INFO] 没有找到状态记录，无需检查")
        return 0

    # 检查自动执行条件
    should_exec, reason = check_auto_exec_condition(state)

    log(f"[CHECK] 检查结果: {reason}")

    if should_exec:
        log("[DECISION] 满足自动执行条件，开始执行...")
        try:
            execute_default_action(state)
            # 执行后重置状态，避免重复执行
            state["auto_executed"] = True
            state["auto_exec_time"] = datetime.now(timezone.utc).timestamp()
            # 这里可以选择是否保存状态，取决于业务需求
            log("[SUCCESS] 自动执行流程完成")
        except Exception as e:
            log(f"[ERROR] 自动执行失败: {e}")
            return 1
    else:
        log("[INFO] 不满足自动执行条件，跳过执行")

    log("=" * 60)
    log("检查完成")
    log("=" * 60)
    return 0

if __name__ == "__main__":
    sys.exit(main())


__all__ = ['log', 'load_state', 'check_auto_exec_condition', 'execute_default_action', 'main']
