#!/usr/bin/env python3
"""
MiniMax API Usage Monitor - 白银规则版本
直接调用 session_status 获取正确 usage 数据
"""
import subprocess
import re
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

LOG_FILE = Path("/Users/fhjtech/.openclaw/workspace/.logs/usage_monitor.log")
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

TZ_CST = timezone(timedelta(hours=8))

def get_session_status():
    """调用 openclaw CLI 获取 session_status JSON 输出"""
    try:
        # openclaw status --json 可能不直接支持，改用 grep 解析
        result = subprocess.run(
            ["/Users/fhjtech/.nvm/versions/node/v24.13.1/bin/openclaw", "status", "--json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout
    except Exception as e:
        return None

def parse_usage_from_status_json(json_str):
    """
    从 openclaw status --json 解析 usage
    查找 "5h XX% left" 格式
    """
    if not json_str:
        return None
    
    # 尝试从原始文本中查找 "5h XX% left" 格式
    match = re.search(r'5h\s+(\d+)%\s*left', json_str)
    if match:
        left_pct = int(match.group(1))
        return 100 - left_pct, left_pct
    
    # 尝试解析 JSON 中的 usage 字段
    try:
        data = json.loads(json_str)
        # 可能在某个嵌套字段中
        def find_usage(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if 'usage' in key.lower() or '5h' in str(value):
                        if isinstance(value, (int, float)):
                            return value
                    result = find_usage(value)
                    if result:
                        return result
            elif isinstance(obj, list):
                for item in obj:
                    result = find_usage(item)
                    if result:
                        return result
            return None
        usage = find_usage(data)
        if usage:
            return usage, None
    except:
        pass
    
    return None, None

def main():
    now = datetime.now(TZ_CST)
    now_str = now.strftime("%m-%d %H:%M")
    
    status_json = get_session_status()
    
    if not status_json:
        print(f"📊 MiniMax | {now_str} | ⚠️ 获取失败")
        with open(LOG_FILE, "a") as f:
            f.write(f"[{now_str}] ERROR: Failed to get status\n")
        return
    
    usage_pct, left_pct = parse_usage_from_status_json(status_json)
    
    if usage_pct is None:
        # 备用：尝试解析纯文本输出
        result = subprocess.run(
            ["/Users/fhjtech/.nvm/versions/node/v24.13.1/bin/openclaw", "status"],
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout + result.stderr
        
        # 查找 "5h XX% left" 或 "XX% left"
        match = re.search(r'(\d+)h\s+(\d+)%\s*left', output)
        if match:
            hours = int(match.group(1))
            left_pct = int(match.group(2))
            usage_pct = 100 - left_pct
        else:
            match = re.search(r'(\d+)%\s*left', output)
            if match:
                left_pct = int(match.group(1))
                usage_pct = 100 - left_pct
    
    if usage_pct is not None:
        reduce_mode = usage_pct >= 95
        emoji = "🟢" if usage_pct < 80 else ("🟡" if usage_pct < 95 else "🔴")
        status = "限流" if reduce_mode else "正常"
        
        print(f"📊 MiniMax | {now_str} | {emoji} 5h窗口 {usage_pct}%已用 | {status}")
        
        with open(LOG_FILE, "a") as f:
            f.write(f"[{now_str}] Usage: {usage_pct}% ({left_pct}% left) | {'REDUCE' if reduce_mode else 'NORMAL'}\n")
        
        # 设置标志
        alert_file = Path("/Users/fhjtech/.openclaw/workspace/.logs/usage_alert.flag")
        if reduce_mode:
            alert_file.write_text(f"{now_str} | Usage: {usage_pct}%\n")
        else:
            if alert_file.exists():
                alert_file.unlink()
    else:
        print(f"📊 MiniMax | {now_str} | ⚠️ 无法解析 usage")
        with open(LOG_FILE, "a") as f:
            f.write(f"[{now_str}] ERROR: Cannot parse usage\n")

if __name__ == "__main__":
    main()
