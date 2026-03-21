#!/usr/bin/env python3
"""
Feishu Message Delivery Confirmation Script
Solution 2: Active polling fallback for message delivery

检查最近一次机器人发送的消息是否有用户回复。
如果没有，在 30 秒后发送一条提醒。
"""

import json
import time
import os
import sys
from datetime import datetime, timezone, timedelta
from urllib.request import Request, urlopen
from urllib.parse import urlencode

# ── 配置 ──────────────────────────────────────────────
APP_ID     = "cli_a90c7258f9b85bef"
APP_SECRET = "Kv6kG5ggU2TP9Ocw5CHSucu1B1t26J7t"
USER_OPEN_ID = "ou_7bc224841d2a1064cf5a7fbf67824227"  # James
BOT_OPEN_ID  = "ou_d34cd8fa5140ad55ff08887fefe76401"  # Harvey bot
BOT_APP_ID   = "cli_a90c7258f9b85bef"                  # Harvey bot app_id

STATE_FILE  = os.path.join(os.path.dirname(__file__), ".feishu_reminder_state.json")
REMINDER_THRESHOLD_SEC = 30   # 机器人发消息后等待用户回复的秒数
MAX_MESSAGES_PER_CHECK = 5   # 每次最多检查几条消息

# ── Feishu API 工具 ───────────────────────────────────
def get_tenant_access_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode()
    req = Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(req, timeout=10) as resp:
        data = json.load(resp)
    if data.get("code") != 0:
        raise Exception(f"Failed to get token: {data}")
    return data["tenant_access_token"]

def get_im_messages(token, chat_id, page_size=MAX_MESSAGES_PER_CHECK):
    """获取指定会话的最新消息"""
    url = f"https://open.feishu.cn/open-apis/im/v1/messages?container_id_type=chat&container_id={chat_id}&page_size={page_size}&sort_type=ByCreateTimeDesc"
    req = Request(url, headers={"Authorization": f"Bearer {token}"})
    with urlopen(req, timeout=10) as resp:
        data = json.load(resp)
    if data.get("code") != 0:
        raise Exception(f"Failed to get messages: {data}")
    return data.get("data", {}).get("items", [])

def send_text_message(token, receive_id, receive_id_type, content):
    """发送文本消息"""
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    payload = {
        "receive_id": receive_id,
        "msg_type": "text",
        "content": json.dumps({"text": content}),
        "receive_id_type": receive_id_type
    }
    data = json.dumps(payload).encode()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    req = Request(url, data=data, headers=headers, method="POST")
    with urlopen(req, timeout=10) as resp:
        return json.load(resp)

def get_or_create_p2p_chat_id(token, user_id):
    """获取或创建与指定用户的 p2p 会话 chat_id"""
    # 方法1: 尝试获取已存在的 p2p 会话
    url = f"https://open.feishu.cn/open-apis/im/v1/chats?user_id_type=open_id&page_size=50"
    req = Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urlopen(req, timeout=10) as resp:
            data = json.load(resp)
        if data.get("code") == 0:
            items = data.get("data", {}).get("items", [])
            for chat in items:
                if chat.get("chat_type") == "p2p":
                    members = chat.get("members", [])
                    if any(m.get("member_id") == user_id for m in members):
                        print(f"[{datetime.now()}] [INFO] Found existing p2p chat: {chat.get('chat_id')}")
                        return chat.get("chat_id")
    except Exception as e:
        print(f"[{datetime.now()}] [WARN] get chats API failed: {e}")

    # 方法2: 尝试直接查询用户信息获取 p2p chat
    url2 = f"https://open.feishu.cn/open-apis/contact/v3/users/{user_id}?user_id_type=open_id"
    req2 = Request(url2, headers={"Authorization": f"Bearer {token}"})
    try:
        with urlopen(req2, timeout=10) as resp:
            data2 = json.load(resp)
        if data2.get("code") == 0:
            print(f"[{datetime.now()}] [INFO] User info: {data2.get('data', {}).get('user', {}).get('name')}")
    except Exception as e:
        print(f"[{datetime.now()}] [WARN] get user API failed: {e}")

    # 方法3: 使用已知会话 ID（从 Gateway 日志中获取）
    KNOWN_P2P_CHAT_ID = "oc_59e5938f0f0e1f3e34dcf84f8ffbc3b7"
    print(f"[{datetime.now()}] [INFO] Using known p2p chat_id: {KNOWN_P2P_CHAT_ID}")
    return KNOWN_P2P_CHAT_ID

# ── 状态管理 ───────────────────────────────────────────
def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {"last_bot_msg_id": None, "last_bot_msg_time": None, "reminder_sent": False}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

# ── 主逻辑 ─────────────────────────────────────────────
def main():
    try:
        token = get_tenant_access_token()
    except Exception as e:
        print(f"[{datetime.now()}] [ERROR] Failed to get token: {e}")
        sys.exit(1)

    # 获取与 James 的 p2p chat_id
    try:
        chat_id = get_or_create_p2p_chat_id(token, USER_OPEN_ID)
    except Exception as e:
        print(f"[{datetime.now()}] [WARN] Failed to get chat_id: {e}")
        chat_id = "oc_59e5938f0f0e1f3e34dcf84f8ffbc3b7"

    if not chat_id:
        print(f"[{datetime.now()}] [ERROR] Cannot find p2p chat_id for user")
        sys.exit(1)

    try:
        messages = get_im_messages(token, chat_id, MAX_MESSAGES_PER_CHECK)
    except Exception as e:
        print(f"[{datetime.now()}] [ERROR] Failed to get messages: {e}")
        sys.exit(1)

    if not messages:
        print(f"[{datetime.now()}] [INFO] No messages found")
        sys.exit(0)

    state = load_state()
    now = time.time()
    tz_cst = timezone(timedelta(hours=8))

    # 按时间正序（ oldest → newest ）处理消息
    # messages 是按 CreateTimeDesc 返回的，所以最后一个是最新的
    messages_asc = list(reversed(messages))

    print(f"[{datetime.now()}] [INFO] Checked {len(messages_asc)} messages, last msg type={messages_asc[-1].get('msg_type')}, sender={messages_asc[-1].get('sender', {}).get('id')} ")

    # 遍历消息，找到最新一条来自机器人的消息
    latest_bot_msg = None
    for msg in reversed(messages_asc):
        sender     = msg.get("sender", {})
        sender_id  = sender.get("id")
        sender_type = sender.get("sender_type", "")
        # 机器人消息: sender_type=app（通过 OpenClaw 发送），或 id 为 bot open_id
        if sender_id == BOT_OPEN_ID or sender_id == BOT_APP_ID or sender_type == "app":
            latest_bot_msg = msg
            break

    if latest_bot_msg:
        msg_id = latest_bot_msg.get("message_id")
        create_time = int(latest_bot_msg.get("create_time", 0)) / 1000  # 毫秒 → 秒
        age_sec = now - create_time

        print(f"[{datetime.now()}] [INFO] Latest bot msg id={msg_id}, age={age_sec:.1f}s, reminder_sent={state['reminder_sent']}")

        if age_sec >= REMINDER_THRESHOLD_SEC and not state["reminder_sent"]:
            # 检查这条消息之后是否有用户回复
            bot_msg_index = None
            for i, msg in enumerate(messages_asc):
                if msg.get("message_id") == msg_id:
                    bot_msg_index = i
                    break

            has_user_reply = False
            if bot_msg_index is not None:
                for msg in messages_asc[bot_msg_index + 1:]:
                    sender_id = msg.get("sender", {}).get("id")
                    if sender_id == USER_OPEN_ID:
                        has_user_reply = True
                        break

            if not has_user_reply:
                ts = datetime.fromtimestamp(create_time, tz=tz_cst).strftime("%H:%M:%S")
                reminder_text = (
                    f"📬 您好！我在 {ts} 发送了一条消息，"
                    f"还没有收到您的回复。如果您看到了我的消息，请忽略此提醒。\n"
                    f"如果没有看到，欢迎随时告诉我！"
                )
                try:
                    result = send_text_message(token, USER_OPEN_ID, "open_id", reminder_text)
                    if result.get("code") == 0:
                        state["reminder_sent"] = True
                        state["last_bot_msg_id"] = msg_id
                        state["last_bot_msg_time"] = create_time
                        save_state(state)
                        print(f"[{datetime.now()}] [OK] Reminder sent successfully")
                    else:
                        print(f"[{datetime.now()}] [ERROR] Failed to send reminder: {result}")
                except Exception as e:
                    print(f"[{datetime.now()}] [ERROR] Exception sending reminder: {e}")
            else:
                print(f"[{datetime.now()}] [INFO] User has replied, skip reminder")
                state["reminder_sent"] = True
                state["last_bot_msg_id"] = msg_id
                state["last_bot_msg_time"] = create_time
                save_state(state)
        elif age_sec < REMINDER_THRESHOLD_SEC:
            # 新消息刚发出去，重置 reminder_sent
            if state["reminder_sent"]:
                print(f"[{datetime.now()}] [INFO] New bot message detected, reset reminder state")
            state["reminder_sent"] = False
            save_state(state)
    else:
        print(f"[{datetime.now()}] [INFO] No bot message found in recent {MAX_MESSAGES_PER_CHECK} messages")

if __name__ == "__main__":
    main()
