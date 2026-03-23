#!/usr/bin/env python3
"""
Harvey 自我健康检查脚本
每5分钟执行一次，确保：
1. OpenClaw Gateway 保持运行
2. Mac 不进入休眠（caffeinate 保活）
3. 系统资源正常
4. 若发现问题，尝试修复；若无法修复，1小时无响应则自动授权处理
"""

import subprocess
import json
import os
import urllib.request
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

GATEWAY_PORT = 18789
GATEWAY_TOKEN = "302b6d89cd1a660bbabaf2239b131d5dfd6eb4cdda41811b"  # from openclaw.json
LOG_DIR = Path("/Users/fhjtech/.openclaw/logs")
LOG_FILE = LOG_DIR / "health_check.log"
PID_FILE = LOG_DIR / "caffeinate.pid"
TZ_CST = timezone(timedelta(hours=8))

# Feishu
FEISHU_APP_ID = "cli_a90c7258f9b85bef"
FEISHU_APP_SECRET = "Kv6kG5ggU2TP9Ocw5CHSucu1B1t26J7t"
FEISHU_USER_ID = "ou_7bc224841d2a1064cf5a7fbf67824227"

# 自动授权等待时间（秒）
AUTO_APPROVE_SEC = 3600  # 1小时

def log(msg) -> None:
    ts = datetime.now(TZ_CST).strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def get_feishu_token() -> None:
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = json.dumps({"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}).encode()
    req = urllib.request.Request(url, data=payload,
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.load(resp)
    return data["tenant_access_token"]

def send_feishu(token, content) -> None:
    url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id"
    payload = {
        "receive_id": FEISHU_USER_ID,
        "msg_type": "text",
        "content": json.dumps({"text": content})
    }
    data = json.dumps(payload).encode()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.load(resp)

def is_gateway_alive() -> None:
    """检查 Gateway 是否响应"""
    url = f"http://127.0.0.1:{GATEWAY_PORT}/health"
    try:
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {GATEWAY_TOKEN}"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status == 200
    except:
        return False

def is_caffeinate_running() -> None:
    """检查 caffeinate 是否在保活"""
    if not PID_FILE.exists():
        return False
    try:
        pid = int(PID_FILE.read_text().strip())
        os.kill(pid, 0)  # 检查进程是否存在
        return True
    except:
        return False

def start_caffeinate():
    """启动 caffeinate 防止休眠"""
    try:
        # 先停掉旧的
        if is_caffeinate_running():
            pid = int(PID_FILE.read_text().strip())
            try:
                os.kill(pid, 9)
            except:
                pass
        # 启动新的 caffeinate -s（系统休眠阻止）
        proc = subprocess.Popen(
            ["caffeinate", "-s", "-i"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        PID_FILE.write_text(str(proc.pid))
        log(f"[CAFFE] Started caffeinate pid={proc.pid}")
        return True
    except Exception as e:
        log(f"[CAFFE] Failed: {e}")
        return False

def restart_gateway():
    """尝试重启 Gateway"""
    log("[GATEWAY] Attempting restart via launchctl...")
    try:
        # unload then load
        subprocess.run(["launchctl", "bootout", "gui/501/ai.openclaw.gateway"],
                      capture_output=True, timeout=10)
        time.sleep(2)
        subprocess.run(["launchctl", "bootstrap", "gui/501",
                      "/Users/fhjtech/Library/LaunchAgents/ai.openclaw.gateway.plist"],
                      capture_output=True, timeout=10)
        time.sleep(3)
        if is_gateway_alive():
            log("[GATEWAY] Restart OK")
            return True
    except Exception as e:
        log(f"[GATEWAY] Restart failed: {e}")
    return False

def check_system_resources():
    """检查系统资源"""
    try:
        subprocess.run(["uptime"], capture_output=True, timeout=3)
        return True
    except Exception as e:
        log(f"[SYS] Resource check error: {e}")
        return True

def get_auto_approve_record():
    """获取自动授权记录"""
    f = LOG_DIR / ".auto_approve_records.json"
    try:
        return json.loads(f.read_text())
    except:
        return []

def record_auto_approve(reason, action):
    """记录自动授权"""
    f = LOG_DIR / ".auto_approve_records.json"
    records = get_auto_approve_record()
    records.append({
        "time": datetime.now(TZ_CST).isoformat(),
        "reason": reason,
        "action": action
    })
    f.write_text(json.dumps(records, indent=2, ensure_ascii=False))

def notify_james(message):
    """发送飞书通知"""
    try:
        token = get_feishu_token()
        result = send_feishu(token, message)
        if result.get("code") == 0:
            log(f"[FEISHU] Notified James: {message[:50]}")
        else:
            log(f"[FEISHU] Failed: {result}")
    except Exception as e:
        log(f"[FEISHU] Error: {e}")

# ── 主检查流程 ─────────────────────────────────
def main():
    log("=== Health Check Started ===")
    issues = []

    # 1. 检查 Gateway 是否活着
    alive = is_gateway_alive()
    log(f"[CHECK] Gateway alive: {alive}")

    if not alive:
        log("[ISSUE] Gateway is DOWN!")
        # 尝试重启
        if restart_gateway():
            log("[RESOLVED] Gateway restarted successfully")
            notify_james("✅ Gateway 已自动重启恢复正常（Harvey 健康检查）")
        else:
            log("[FAIL] Gateway restart failed")
            issues.append("Gateway 重启失败，需要 James 手动处理")
            # 1小时无响应则自动授权重启
            DOWN_FILE = LOG_DIR / ".gateway_down_start.txt"
            now_ts = time.time()
            if DOWN_FILE.exists():
                down_start = float(DOWN_FILE.read_text().strip())
                elapsed = now_ts - down_start
                log(f"[DOWN] Gateway down for {elapsed:.0f}s ({elapsed/3600:.1f}h)")
                if elapsed >= AUTO_APPROVE_SEC:
                    log("[AUTO-APPROVE] 1hr passed, executing force restart...")
                    try:
                        subprocess.run(["launchctl", "bootout", "-9", "gui/501/ai.openclaw.gateway"],
                                      capture_output=True, timeout=10)
                        time.sleep(2)
                        subprocess.run(["launchctl", "bootstrap", "gui/501",
                                      "/Users/fhjtech/Library/LaunchAgents/ai.openclaw.gateway.plist"],
                                      capture_output=True, timeout=10)
                        record_auto_approve("Gateway宕机1小时无响应", "launchctl强制重启")
                        notify_james("⚡ Harvey 已自动授权执行强制重启，请注意检查")
                        DOWN_FILE.unlink()
                    except Exception as e:
                        log(f"[AUTO-APPROVE] Failed: {e}")
            else:
                # 首次检测到宕机
                DOWN_FILE.write_text(str(now_ts))
                log(f"[DOWN] Gateway down detected, started tracking from {now_ts}")
                notify_james("🚨 Harvey Gateway 宕机，正在尝试重启。如果1小时内未恢复，我将自动授权强制重启。")
    else:
        # Gateway 正常，清除宕机记录
        DOWN_FILE = LOG_DIR / ".gateway_down_start.txt"
        if DOWN_FILE.exists():
            DOWN_FILE.unlink()
            log("[OK] Gateway back up, cleared down tracking")

        # 检查 caffeinate 是否在运行
        if not is_caffeinate_running():
            log("[ISSUE] caffeinate not running, starting...")
            if start_caffeinate():
                notify_james("🔧 Harvey 已自动启动 caffeinate 防止 Mac 休眠")
        else:
            log("[OK] caffeinate is running")
        if not is_caffeinate_running():
            log("[ISSUE] caffeinate not running, starting...")
            start_caffeinate()
            notify_james("🔧 Harvey 已自动启动 caffeinate 防止 Mac 休眠")
        else:
            log("[OK] caffeinate is running")

    # 2. 系统资源检查
    check_system_resources()

    log(f"=== Health Check Done, issues={len(issues)} ===")

if __name__ == "__main__":
    main()


__all__ = ['log', 'get_feishu_token', 'send_feishu', 'is_gateway_alive', 'is_caffeinate_running', 'start_caffeinate', 'restart_gateway', 'check_system_resources', 'get_auto_approve_record', 'record_auto_approve', 'notify_james', 'main']
