#!/usr/bin/env python3
"""
1小时无回复自动执行检查器
检查最后发送的消息是否在1小时内收到回复，如无则自动执行默认操作
"""

import json
import os
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

def log(message):
    """记录日志"""
    ts = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{ts}] {message}"
    print(log_message)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_message + "\n")

def load_state():
    """加载提醒状态"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            log(f"[ERROR] 加载状态文件失败: {e}")
    return {}

def check_auto_exec_condition(state):
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

def execute_default_action():
    """
    执行默认自动操作
    这里可以根据需要配置具体的执行逻辑
    """
    log("[ACTION] 开始执行默认自动操作...")
    
    # TODO: 根据具体业务需求实现自动执行逻辑
    # 例如：
    # 1. 执行预设的命令或脚本
    # 2. 发送执行确认通知
    # 3. 更新任务状态
    # 4. 触发后续工作流
    
    # 示例：记录执行日志
    execution_record = {
        "timestamp": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        "action": "auto_execute_default",
        "trigger": "1_hour_no_reply",
        "status": "completed"
    }
    
    # 可以保存到执行记录文件或数据库
    exec_log_file = os.path.join(WORKSPACE, ".logs", "auto_exec_history.jsonl")
    os.makedirs(os.path.dirname(exec_log_file), exist_ok=True)
    with open(exec_log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(execution_record, ensure_ascii=False) + "\n")
    
    log("[ACTION] 默认自动操作执行完成")
    return True

def main():
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
            execute_default_action()
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
