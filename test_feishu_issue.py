#!/usr/bin/env python3
"""
Test Feishu integration and message delivery
"""
import json
import sys
import os
from datetime import datetime, timezone, timedelta

# Add workspace to path
sys.path.insert(0, '/Users/fhjtech/.openclaw/workspace/email_integration')

def test_state_file():
    """Check state file status"""
    state_path = '/Users/fhjtech/.openclaw/workspace/email_integration/.feishu_reminder_state.json'
    
    print("=" * 60)
    print("1. 检查状态文件")
    print("=" * 60)
    
    if os.path.exists(state_path):
        with open(state_path, 'r') as f:
            state = json.load(f)
        print(f"状态文件路径: {state_path}")
        print(f"上次提醒时间: {state.get('last_reminder_time', 'None')}")
        print(f"提醒次数: {state.get('reminder_count', 0)}")
        return state
    else:
        print(f"状态文件不存在: {state_path}")
        return None

def test_cron_jobs():
    """Check what cron jobs are running"""
    print("\n" + "=" * 60)
    print("2. 检查 Cron 任务")
    print("=" * 60)
    
    import subprocess
    try:
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'feishu' in line.lower() or 'delivery' in line.lower():
                    print(f"  飞书检查任务: {line}")
                elif 'self_health' in line.lower():
                    print(f"  健康检查任务: {line}")
        else:
            print("无法读取 crontab")
    except Exception as e:
        print(f"检查 cron 时出错: {e}")

def test_feishu_module():
    """Test if Feishu module can be imported"""
    print("\n" + "=" * 60)
    print("3. 测试 Feishu 模块导入")
    print("=" * 60)
    
    try:
        # Check if feishu module exists
        feishu_doc_path = '/Users/fhjtech/.openclaw/workspace/.agents/skills/feishu-doc/SKILL.md'
        if os.path.exists(feishu_doc_path):
            print(f"✓ feishu-doc skill 存在: {feishu_doc_path}")
        else:
            print(f"✗ feishu-doc skill 不存在")
        
        # Check OpenClaw tools
        print("\n检查 OpenClaw 工具可用性:")
        print("  - 使用 feishu_chat 工具检查消息")
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")

def analyze_time_range():
    """Analyze the time range from 5 PM yesterday to now"""
    print("\n" + "=" * 60)
    print("4. 时间范围分析")
    print("=" * 60)
    
    now = datetime.now(timezone(timedelta(hours=8)))  # Shanghai time
    yesterday_5pm = now.replace(hour=17, minute=0, second=0, microsecond=0) - timedelta(days=1)
    
    print(f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')} (Shanghai)")
    print(f"调查起始: {yesterday_5pm.strftime('%Y-%m-%d %H:%M:%S')} (Shanghai)")
    print(f"时间跨度: {(now - yesterday_5pm).total_seconds() / 3600:.1f} 小时")

def check_session_status():
    """Check if there are active sessions"""
    print("\n" + "=" * 60)
    print("5. 会话状态检查")
    print("=" * 60)
    
    # Check if OpenClaw is running
    import subprocess
    try:
        result = subprocess.run(['pgrep', '-f', 'openclaw'], capture_output=True, text=True)
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            print(f"✓ OpenClaw 进程运行中 (PID: {', '.join(pids[:5])})")
        else:
            print("✗ OpenClaw 进程未运行")
    except Exception as e:
        print(f"无法检查进程: {e}")

def main():
    print("=" * 60)
    print("Feishu 消息不回复问题诊断")
    print("=" * 60)
    
    test_state_file()
    test_cron_jobs()
    test_feishu_module()
    analyze_time_range()
    check_session_status()
    
    print("\n" + "=" * 60)
    print("诊断总结")
    print("=" * 60)
    print("""
初步发现:
1. feishu_delivery_check.py 每分钟运行，检查最后消息时间
2. 如果消息超过 120 秒未回复，会发送提醒
3. 状态文件显示 reminder_count=0，说明提醒机制未触发或重置过

需要进一步调查:
- OpenClaw 网关是否正常运行
- Feishu 消息是否被正确接收和处理
- 是否有会话被阻塞或卡死
""")

if __name__ == "__main__":
    main()
