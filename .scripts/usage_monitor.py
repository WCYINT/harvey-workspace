#!/usr/bin/env python3
"""
MiniMax Usage Monitor - Session Status 版本
⚠️ 注意：MiniMax API 数据来源已移除（James 2026-04-04 确认数据不准，存在误读）
权威数据源：session_status 命令的输出
"""
from datetime import datetime, timezone, timedelta
from pathlib import Path

LOG_FILE = Path("/Users/fhjtech/.openclaw/logs/usage_monitor.log")
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

TZ_CST = timezone(timedelta(hours=8))

def main() -> None:
    now = datetime.now(TZ_CST)
    now_str = now.strftime("%m-%d %H:%M")
    
    # MiniMax API 数据来源已移除
    # 权威数据源：session_status 命令
    # James 确认：以 OpenClaw 控制台 session_status 输出为准
    
    msg = f"📊 MiniMax | {now_str} | ℹ️ API监控已停用 | 以 session_status 为准"
    print(msg)
    
    with open(LOG_FILE, "a") as f:
        f.write(f"[{now_str}] NOTE: MiniMax API monitoring disabled (James 2026-04-04: data inaccurate)\n")
        f.write(f"         Use session_status command for accurate usage data\n")

if __name__ == "__main__":
    main()


__all__ = ['main']
