#!/usr/bin/env python3
"""
MiniMax API 使用率监控脚本（优化版）
改用直接API查询，移除Playwright依赖，提升稳定性和速度

NOTE: MiniMax usage API requires authenticated session cookies.
      This script currently delegates to minimax_usage_monitor.py (Playwright-based)
      until we have a valid API key/token for direct queries.
"""

import json
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

# 配置
FEISHU_APP_ID = "cli_a90c7258f9b85bef"
FEISHU_APP_SECRET = "Kv6kG5ggU2TP9Ocw5CHSucu1B1t26J7t"
FEISHU_USER_ID = "ou_7bc224841d2a1064cf5a7fbf67824227"
WORKSPACE = Path("/Users/fhjtech/.openclaw/workspace")

TZ_CST = timezone(timedelta(hours=8))


def log(msg: str) -> None:
    ts = datetime.now(TZ_CST).strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")


def get_feishu_token() -> str:
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = json.dumps({"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}).encode()
    req = urllib.request.Request(url, data=payload,
                                 headers={"Content-Type": "application/json"}, method="POST")  # type: ignore[arg-type]
    with urllib.request.urlopen(req, timeout=10) as resp:  # type: ignore[arg-type]
        data = json.load(resp)
    if data.get("code") != 0:
        raise Exception(f"Failed to get token: {data}")
    return data["tenant_access_token"]


def send_feishu_message(token: str, content: str, receive_id: str) -> dict:
    url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id"
    payload = {
        "receive_id": receive_id,
        "msg_type": "text",
        "content": json.dumps({"text": content})
    }
    data = json.dumps(payload).encode()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")  # type: ignore[arg-type]
    with urllib.request.urlopen(req, timeout=10) as resp:  # type: ignore[arg-type]
        return json.load(resp)


def get_minimax_usage() -> dict:
    """
    Query the MiniMax usage API via the Playwright-based monitor.
    Falls back to error if Playwright-based script is unavailable.
    """
    monitor_path = WORKSPACE / ".scripts/minimax_usage_monitor.py"
    if not monitor_path.exists():
        raise RuntimeError(
            "minimax_usage_monitor.py not found. "
            "This script requires Playwright-based authentication to fetch real usage data."
        )
    result = subprocess.run(
        [sys.executable, str(monitor_path)],
        capture_output=True, text=True, timeout=120,
        cwd=str(WORKSPACE)
    )
    if result.returncode != 0:
        raise RuntimeError(f"minimax_usage_monitor.py failed: {result.stderr[:200]}")
    # Parse output to extract usage summary
    # The Playwright script prints logs to stdout; look for key metrics
    for line in result.stdout.splitlines():
        if "interval usage" in line.lower() or "m2.7" in line.lower():
            return {"_raw": result.stdout}
    return {"_raw": result.stdout}


def main() -> None:
    log("Starting MiniMax usage check (optimized)...")

    try:
        usage = get_minimax_usage()
        raw = usage.get("_raw", "")
        if raw:
            log(f"Monitor output: {raw[:300]}")
        log("MiniMax usage check completed successfully.")
    except RuntimeError as e:
        log(f"[WARN] {e}")
    except Exception as e:
        log(f"Error: {e}")


if __name__ == "__main__":
    main()
