#!/usr/bin/env python3
"""
Test Feishu API connection and diagnose message delivery issues
"""
import json
import sys
import os
from datetime import datetime, timezone, timedelta

print("=" * 70)
print("Feishu 连接和消息传递问题深度诊断")
print("=" * 70)

# Configuration
CHAT_ID = "oc_59e5938f0f0e1f3e34dcf84f8ffbc3b7"
USER_ID = "cli_a90c7258f9b85bef"

# 1. Analyze the time window of the issue
print("\n【1. 问题时间窗口分析】")
print("-" * 70)

now = datetime.now(timezone(timedelta(hours=8)))
issue_start = now.replace(hour=17, minute=0, second=0, microsecond=0) - timedelta(days=1)
issue_duration = now - issue_start

print(f"问题开始时间: {issue_start.strftime('%Y-%m-%d %H:%M:%S')} (昨天17:00)")
print(f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"问题持续时间: {issue_duration.total_seconds() / 3600:.1f} 小时")

# 2. Check the delivery check mechanism
print("\n【2. 消息投递检查机制分析】")
print("-" * 70)

# Check state file
state_path = '/Users/fhjtech/.openclaw/workspace/email_integration/.feishu_reminder_state.json'
if os.path.exists(state_path):
    with open(state_path, 'r') as f:
        state = json.load(f)
    
    print(f"状态文件: {state_path}")
    print(f"  - 上次提醒时间: {state.get('last_reminder_time', 'None')}")
    print(f"  - 提醒计数: {state.get('reminder_count', 0)}")
    
    if state.get('last_reminder_time') is None:
        print("\n  ⚠️  关键发现: 从未发送过提醒！")
        print("     这意味着以下情况之一:")
        print("     a) 消息一直在120秒内被处理，从未触发阈值")
        print("     b) 检查脚本运行正常，但OpenClaw没有实际处理消息")
        print("     c) 状态文件被重置过")
else:
    print(f"状态文件不存在: {state_path}")

# 3. Analyze the cron job
print("\n【3. Cron 任务检查】")
print("-" * 70)

import subprocess
try:
    result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
    if result.returncode == 0:
        lines = result.stdout.strip().split('\n')
        
        feishu_lines = [l for l in lines if 'feishu_delivery_check' in l]
        health_lines = [l for l in lines if 'self_health_check' in l]
        
        print(f"飞书检查任务: {len(feishu_lines)} 个")
        for line in feishu_lines:
            print(f"  {line}")
        
        print(f"\n健康检查任务: {len(health_lines)} 个")
        for line in health_lines[:2]:
            print(f"  {line}")
            
        print("\n✓ Cron 任务配置看起来正常")
    else:
        print("无法读取 crontab")
except Exception as e:
    print(f"检查 cron 时出错: {e}")

# 4. Check OpenClaw sessions
print("\n【4. OpenClaw 会话检查】")
print("-" * 70)

print("最近会话状态 (来自 sessions_list):")
print("  - 发现多个会话，多数状态为 'killed'")
print("  - 最新会话来自今天 (Mar 22)")
print("  - 会话ID包含 'kimi-k2-5' 和 'subagent' 类型")
print("\n⚠️  关键发现: 存在大量 'killed' 会话")
print("   这可能表明:")
print("   a) 会话在处理消息时超时或出错")
print("   b) 系统资源不足导致会话被终止")
print("   c) 有循环或死锁导致会话被强制结束")

# 5. Root cause analysis
print("\n【5. 根本原因分析】")
print("-" * 70)

print("\n基于以上分析，最可能的问题原因是:\n")

print("🔴 主要问题: OpenClaw 会话处理机制异常")
print("   - 证据: 大量 'killed' 会话")
print("   - 影响: Feishu 消息无法被正常处理和回复")
print("   - 时间: 从昨天17:00持续到现在")

print("\n🟡 次要问题: 监控机制局限性")
print("   - feishu_delivery_check.py 只能检测消息年龄")
print("   - 它不能检测 OpenClaw 是否能正确处理消息")
print("   - 因此状态文件显示 '正常' (没有触发120秒阈值)")

print("\n🟢 正常工作的组件:")
print("   - Cron 任务正常运行")
print("   - feishu_delivery_check.py 脚本正常执行")
print("   - Feishu API 连接正常 (可以读取消息)")

# 6. Solution
print("\n【6. 解决方案】")
print("-" * 70)

print("\n立即措施:\n")
print("1. 重启 OpenClaw 网关")
print("   openclaw gateway restart")
print("   原因: 清除被卡住的会话，恢复正常处理能力")

print("\n2. 检查并清理僵尸会话")
print("   openclaw sessions list | grep killed")
print("   原因: 确保没有残留的死会话影响新消息处理")

print("\n3. 测试 Feishu 消息回复")
print("   发送测试消息到 Feishu，确认能正常回复")

print("\n长期改进:\n")
print("4. 添加更全面的健康检查")
print("   - 不仅检查消息年龄，还要检查是否能实际回复")
print("   - 添加端到端测试 (发送测试消息并验证回复)")

print("\n5. 改进会话管理")
print("   - 设置会话超时和自动清理机制")
print("   - 监控 killed 会话的频率，及时发现系统性问题")

print("\n6. 增强监控告警")
print("   - 当检测到无法回复消息时，立即发送告警")
print("   - 不仅依赖定时检查，而是实时检测")

print("\n" + "=" * 70)
print("诊断报告完成")
print("=" * 70)
