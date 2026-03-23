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

def get_recent_sessions() -> None:
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

def count_turns_on_topic(session_file, keywords) -> None:
    """计算特定主题的来回轮次"""
    try:
        with open(session_file, 'r') as f:
            lines = f.readlines()
        
        turns = 0
        consecutive_turns = 0
        max_consecutive = 0
        last_sender = None
        
        for line in lines[-100:]:  # 只看最近100条
            try:
                msg = json.loads(line.strip())
                content = msg.get('content', '')
                sender = msg.get('sender', 'unknown')
                
                # 检查是否包含关键词
                if any(kw.lower() in content.lower() for kw in keywords):
                    if sender != last_sender:
                        consecutive_turns += 1
                        last_sender = sender
                    turns += 1
                    max_consecutive = max(max_consecutive, consecutive_turns)
                else:
                    consecutive_turns = 0
                    last_sender = None
            except (json.JSONDecodeError, KeyError):
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
    
    # 检测关键词
    usage_keywords = ["usage", "百分比", "13%", "8%", "left", "API使用率"]
    turn_count = count_turns_on_topic(recent[0], usage_keywords)
    
    if turn_count > 3:
        log_reflection(
            topic="session_status usage% 解读",
            turns_spent=turn_count,
            summary="误解 '5h 13% left' 格式，将13%理解为剩余而非已用",
            lesson="当James说'只用8%'时，没有立即确认数字来源，而是自行推演。应立即问'这个8%对应session_status哪个字段？'"
        )
    
    print(f"Turns on usage topic: {turn_count}")

if __name__ == "__main__":
    main()


__all__ = ['get_recent_sessions', 'count_turns_on_topic', 'log_reflection', 'main']
