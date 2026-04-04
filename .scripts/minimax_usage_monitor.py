#!/usr/bin/env python3
"""
MiniMax API 使用率监控脚本
自动登录并查询 Token Plan 使用量，通过飞书/元宝通知 James
"""

import json
import os
import time
import urllib.request
from datetime import datetime, timezone, timedelta
from playwright.sync_api import sync_playwright

CHROME_PATH = "/Users/fhjtech/Library/Caches/ms-playwright/chromium-1208/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
USERNAME = "18620362529"
PASSWORD = os.environ.get("MINIMAX_PASSWORD", "WG17sjjlove")
FEISHU_APP_ID = "cli_a90c7258f9b85bef"
FEISHU_APP_SECRET = "Kv6kG5ggU2TP9Ocw5CHSucu1B1t26J7t"
FEISHU_USER_ID = "ou_7bc224841d2a1064cf5a7fbf67824227"
YUANBAO_GROUP_ID = "905675351"

TZ_CST = timezone(timedelta(hours=8))

def log(msg) -> None:
    ts = datetime.now(TZ_CST).strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")

def get_feishu_token() -> str:
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = json.dumps({"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}).encode()
    req = urllib.request.Request(url, data=payload,
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.load(resp)["tenant_access_token"]

def send_feishu_message(token, content, receive_id, receive_id_type="open_id") -> dict:
    url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type={receive_id_type}"
    payload = {
        "receive_id": receive_id,
        "msg_type": "text",
        "content": json.dumps({"text": content})
    }
    data = json.dumps(payload).encode()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.load(resp)

def get_minimax_cookies() -> list:
    """Login to MiniMax and return cookies for API auth"""
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME_PATH, headless=True)
        page = browser.new_page()
        page.goto("https://platform.minimaxi.com/login")
        page.wait_for_timeout(2000)
        page.locator('input[placeholder="请输入手机号/邮箱"]').fill(USERNAME)
        page.locator('input[placeholder="请输入登录密码"]').fill(PASSWORD)
        page.locator('input[type="checkbox"]').check()
        page.locator('button:has-text("立即登录")').click()
        page.wait_for_timeout(5000)
        cookies = page.context.cookies()
        browser.close()
        return cookies

def get_usage(cookies) -> dict:
    """Query the MiniMax usage API"""
    cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
    url = "https://www.minimaxi.com/v1/api/openplatform/coding_plan/remains"
    req = urllib.request.Request(url, headers={
        "Cookie": cookie_str
        # Note: GET request — no Content-Type needed
    })
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())

def format_report(usage_data) -> str:
    """Format usage data into a readable report"""
    now = datetime.now(TZ_CST).strftime("%Y-%m-%d %H:%M")
    
    # Find M2.7 data
    m27_data = None
    for model in usage_data.get("model_remains", []):
        if model["model_name"] == "MiniMax-M2.7":
            m27_data = model
            break
    
    if not m27_data:
        return f"📊 **MiniMax API 使用报告** ({now})\n\n❌ 无法获取数据"
    
    # James 确认（usage_monitor.py 已验证）：
    # current_interval_usage_count = 可用次数（remaining）
    # total - usage_count = 已用次数（used）
    interval_available = m27_data["current_interval_usage_count"]  # API返回=可用次数
    interval_total = m27_data["current_interval_total_count"]
    interval_actual_used = interval_total - interval_available
    interval_pct = interval_actual_used / interval_total * 100
    
    weekly_used = m27_data["current_weekly_usage_count"]
    weekly_total = m27_data["current_weekly_total_count"]
    weekly_pct = weekly_used / weekly_total * 100
    weekly_left = weekly_total - weekly_used
    
    # Determine status emoji
    def status(pct) -> str:
        if pct >= 90: return "🔴"
        if pct >= 70: return "🟡"
        return "🟢"
    
    # 5小时窗口时间范围（固定5小时一个窗口，从start_time到end_time）
    interval_start = datetime.fromtimestamp(m27_data["start_time"] / 1000, tz=TZ_CST)
    interval_end = datetime.fromtimestamp(m27_data["end_time"] / 1000, tz=TZ_CST)
    interval_range = f"{interval_start.strftime('%H:%M')} - {interval_end.strftime('%H:%M')}"
    
    # 剩余时间 = remains_time（毫秒）→ 转换为"还有X小时Y分"
    remains_ms = m27_data["remains_time"]
    remains_hours = int(remains_ms // 1000 // 3600)
    remains_mins = int((remains_ms // 1000 % 3600) // 60)
    remains_str = f"{remains_hours}小时{remains_mins}分" if remains_hours > 0 else f"{remains_mins}分"
    
    # 5小时窗口：API数据（含Cache命中）与网站显示不同
    # James 确认以网站数值为准，网站显示的是纯实际调用消耗
    # API interval_used = 含Cache命中数，网站 = 实际调用（不含Cache）
    # 本周配额使用API数据（网站和API一致）
    report = f"""📊 **MiniMax M2.7 API 使用报告** ({now})

**5小时滚动窗口** {interval_range}（还有{remains_str}自动恢复）:
{status(interval_pct)} 可用约 {interval_available:,} / {interval_total:,} ({100-interval_pct:.1f}%)
   ⚠️ API含Cache命中；网站显示约27%，以网站数值为准
   已用约 {interval_actual_used:,} 次

**本周上限**（周日23:59重置）:
{status(weekly_pct)} 已用 {weekly_used:,} / {weekly_total:,} ({weekly_pct:.1f}%)
   剩余约 {weekly_left:,} 次

💰 账户余额: ¥22.77 + ¥22.83代金券"""
    
    return report

def main() -> None:
    log("Starting MiniMax usage check...")
    
    try:
        # Get fresh cookies (login)
        log("Logging into MiniMax...")
        cookies = get_minimax_cookies()
        log(f"Got {len(cookies)} cookies")
        
        # Get usage data
        log("Querying usage API...")
        usage = get_usage(cookies)
        
        if usage.get("base_resp", {}).get("status_code") != 0:
            log(f"API error: {usage}")
            return
        
        # Format and send report
        report = format_report(usage)
        log("Sending Feishu message...")
        
        token = get_feishu_token()
        
        # Send to James (Feishu DM)
        result = send_feishu_message(token, report, FEISHU_USER_ID, "open_id")
        if result.get("code") == 0:
            log("Report sent to James via Feishu DM")
        else:
            log(f"Failed to send to James: {result}")
        
        # Also send to Yuanbao group (chat_id type)
        try:
            result_yb = send_feishu_message(token, report, YUANBAO_GROUP_ID, "chat_id")
            if result_yb.get("code") == 0:
                log("Report sent to Yuanbao group")
            else:
                log(f"Failed to send to Yuanbao: {result_yb}")
        except Exception as e:
            log(f"Yuanbao send error: {e}")
        
    except Exception as e:
        log(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()


__all__ = ['log', 'get_feishu_token', 'send_feishu_message', 'get_minimax_cookies', 'get_usage', 'format_report', 'main', 'status']
