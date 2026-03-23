#!/usr/bin/env python3
"""
Test Feishu message receiving and response capability
"""
import json
import sys
import os
from datetime import datetime, timezone, timedelta

print("=" * 60)
print("Feishu 消息接收和响应能力测试")
print("=" * 60)

# Test 1: Check if Feishu chat can be accessed
print("\n【测试1】检查 Feishu 聊天访问")
print("-" * 40)

# The chat_id from the delivery check script
CHAT_ID = "oc_59e5938f0f0e1f3e34dcf84f8ffbc3b7"
print(f"聊天ID: {CHAT_ID}")

# Test 2: Simulate what happens when a message arrives
print("\n【测试2】模拟消息接收流程")
print("-" * 40)

# Current time
now = datetime.now(timezone(timedelta(hours=8)))
print(f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")

# Simulate a message arriving 30 seconds ago
msg_time = now - timedelta(seconds=30)
print(f"模拟消息时间: {msg_time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"消息年龄: 30秒")

# Check if this would trigger a reminder (threshold is 120s)
if 30 < 120:
    print("✓ 消息年龄 < 120秒阈值，不会触发提醒")
else:
    print("✗ 消息年龄 >= 120秒阈值，会触发提醒")

# Test 3: Check the gap between 5 PM yesterday and now
print("\n【测试3】分析昨晚5点至今的时间窗口")
print("-" * 40)

yesterday_5pm = now.replace(hour=17, minute=0, second=0, microsecond=0) - timedelta(days=1)
time_diff = now - yesterday_5pm
hours_passed = time_diff.total_seconds() / 3600

print(f"昨晚5点: {yesterday_5pm.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"时间跨度: {hours_passed:.1f} 小时")

# Test 4: Analyze potential issues
print("\n【测试4】潜在问题分析")
print("-" * 40)

issues = []

# Check if OpenClaw is running
import subprocess
try:
    result = subprocess.run(['pgrep', '-f', 'openclaw'], capture_output=True, text=True)
    if result.returncode != 0:
        issues.append("OpenClaw 进程未运行")
except:
    issues.append("无法检查 OpenClaw 进程")

# Check state file
state_path = '/Users/fhjtech/.openclaw/workspace/email_integration/.feishu_reminder_state.json'
if os.path.exists(state_path):
    with open(state_path, 'r') as f:
        state = json.load(f)
    if state.get('reminder_count', 0) == 0:
        print("ℹ️ 状态文件显示提醒计数为0 - 可能提醒系统从未触发或状态被重置")
else:
    issues.append("状态文件不存在")

# Display issues
if issues:
    print("发现的问题:")
    for issue in issues:
        print(f"  ✗ {issue}")
else:
    print("✓ 未发现明显问题")

# Test 5: Check session activity
print("\n【测试5】会话活动检查")
print("-" * 40)

# Check if there are any recent sessions
print("检查最近的会话活动...")
print("提示: 如果 OpenClaw 会话被卡住或没有正确处理消息，可能导致不回复")

# Summary
print("\n" + "=" * 60)
print("测试总结")
print("=" * 60)

print("""
根据测试分析，可能的原因包括:

1. 提醒系统机制问题:
   - feishu_delivery_check.py 只在消息超过120秒时才发送提醒
   - 如果消息一直很快被处理，提醒系统不会触发
   - 但这不是根本原因，只是监控机制

2. OpenClaw 会话问题:
   - 可能存在会话卡死或没有正确处理Feishu消息
   - 需要检查 OpenClaw 网关状态和会话列表

3. Feishu 集成问题:
   - Feishu 配置或token可能过期
   - 需要验证Feishu API连接

建议下一步:
1. 检查 OpenClaw 会话状态
2. 验证 Feishu API 连接
3. 检查是否有错误日志
""")
