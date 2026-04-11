#!/opt/homebrew/bin/python3
"""
Auto Reflection Trigger
当对话中同一问题花费 >3 轮才解决时，自动记录到 learnings/ERRORS.md

工作流程：
1. 读取当前 session 历史
2. 检测是否有 >3 轮对话未解决的模式
3. 如果发现，自动记录反思到 learnings/ERRORS.md
"""

import json
import os
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/Users/fhjtech/.openclaw/workspace")
LEARNINGS_DIR = WORKSPACE / ".learnings"
ERRORS_FILE = LEARNINGS_DIR / "ERRORS.md"

# 最近对话会话目录
SESSIONS_DIR = Path("/Users/fhjtech/.openclaw/agents/main/sessions")

def get_recent_sessions() -> list[Path]:
    """获取最近的 session 文件"""
    if not SESSIONS_DIR.exists():
        return []
    
    sessions = []
    for f in SESSIONS_DIR.glob("*.jsonl"):
        mtime = f.stat().st_mtime
        sessions.append((f, mtime))
    
    # 按修改时间排序，返回最近3个
    sessions.sort(key=lambda x: x[1], reverse=True)
    return [s[0] for s in sessions[:3]]

def count_turns_on_topic(session_file, keywords) -> int:
    """计算特定主题的来回轮次
    
    支持两种 session 格式:
    - OpenClaw v3: {"type":"message","message":{"role":"user|assistant","content":[{"type":"text","text":"..."}]}}
    - Legacy: {"sender":"...","content":"..."}
    """
    try:
        with open(session_file, 'r') as f:
            lines = f.readlines()
        
        consecutive_turns = 0
        max_consecutive = 0
        last_sender = None
        
        for line in lines[-200:]:  # 看最近200条（增加样本量）
            try:
                msg = json.loads(line.strip())
                
                # OpenClaw v3 格式
                if 'message' in msg and 'role' in msg['message']:
                    role = msg['message']['role']
                    # 提取所有文本内容块
                    content_parts = []
                    for block in msg['message'].get('content', []):
                        if isinstance(block, dict) and block.get('type') == 'text':
                            content_parts.append(block.get('text', ''))
                        elif isinstance(block, dict) and block.get('type') == 'toolResult':
                            # toolResult content can be str or list; guard against string iteration
                            tc = block.get('content', [])
                            if isinstance(tc, list):
                                for tb in tc:
                                    if isinstance(tb, dict) and tb.get('type') == 'text':
                                        content_parts.append(tb.get('text', ''))
                            elif isinstance(tc, str):
                                content_parts.append(tc)
                    content = ' '.join(content_parts)
                    sender = role  # "user" or "assistant"
                else:
                    # Legacy 格式
                    content = msg.get('content', '')
                    sender = msg.get('sender', 'unknown')
                
                # 检查是否包含关键词
                has_kw = any(kw.lower() in content.lower() for kw in keywords)
                
                if has_kw:
                    if sender == 'user':
                        # Bug fix: 用户再次发送相同关键词 = 又一轮追问，+1
                        # 原逻辑仅在 assistant 回应后 +1，导致用户连续追问时被漏计
                        if last_sender == 'user':
                            consecutive_turns += 1
                            max_consecutive = max(max_consecutive, consecutive_turns)
                        last_sender = sender
                    elif sender == 'assistant' and last_sender == 'user':
                        # assistant 完成了一个完整 round (user->assistant)，+1
                        consecutive_turns += 1
                        max_consecutive = max(max_consecutive, consecutive_turns)
                        last_sender = sender
                elif sender == 'user':
                    # 非关键词用户消息: 话题切换，彻底重置
                    consecutive_turns = 0
                    last_sender = sender
            except (json.JSONDecodeError, KeyError, TypeError):
                continue
        
        return max_consecutive
    except Exception as e:
        print(f"Error reading session: {e}")
        return 0

def log_reflection(topic, turns_spent, summary, lesson) -> None:
    """记录反思到 ERRORS.md"""
    LEARNINGS_DIR.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    entry = f"""

## 🔄 Auto-Reflection Trigger (自动反思)
- **时间**: {timestamp}
- **话题**: {topic}
- **花费轮次**: {turns_spent} 轮 (>3轮触发)
- **问题摘要**: {summary}
- **教训**: {lesson}
- **预防措施**: 以后遇到类似问题，立即澄清而非自行推演

---
"""
    
    # 追加到文件
    with open(ERRORS_FILE, 'a') as f:
        f.write(entry)
    
    print(f"✅ Auto-reflection logged: {topic} ({turns_spent} turns)")

def main() -> None:
    """主函数"""
    # 检测 usage 相关话题是否花费过多轮次
    recent = get_recent_sessions()
    
    if not recent:
        print("No recent sessions found")
        return
    
    # 检测关键词（遍历所有最近 session，避免跨 session 的重复问题漏检）
    usage_keywords = ["usage", "百分比", "13%", "8%", "left", "API使用率"]
    max_turns = 0
    for session_file in recent:
        turns = count_turns_on_topic(session_file, usage_keywords)
        max_turns = max(max_turns, turns)
    
    if max_turns > 3:
        log_reflection(
            topic="session_status usage% 解读",
            turns_spent=max_turns,
            summary="误解 '5h 13% left' 格式，将13%理解为剩余而非已用",
            lesson="当James说'只用8%'时，没有立即确认数字来源，而是自行推演。应立即问'这个8%对应session_status哪个字段？'"
        )
    
    print(f"Max turns on usage topic (across {len(recent)} sessions): {max_turns}")

if __name__ == "__main__":
    main()


__all__ = ['get_recent_sessions', 'count_turns_on_topic', 'log_reflection', 'main']
