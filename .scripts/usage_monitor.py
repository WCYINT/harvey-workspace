#!/usr/bin/env python3
"""
MiniMax API Usage Monitor - 白银规则版本 v3
监控指标改为：可用次数 / 可用阈值5%
James 确认：当前 630/4500 = 698/4500 = 实际可用次数
"""
import json
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path
from playwright.sync_api import sync_playwright

LOG_FILE = Path("/Users/fhjtech/.openclaw/logs/usage_monitor.log")
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

TZ_CST = timezone(timedelta(hours=8))

MINIMAX_EMAIL = "18620362529"
MINIMAX_PASSWORD = "WG17sjjlove"
THRESHOLD_REMAINING_PCT = 5  # 可用次数低于总量5%时告警

def get_minimax_cookies():
    """使用 Playwright 登录 MiniMax 获取 cookies"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None

    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        page = browser.new_page()
        
        try:
            page.goto('https://platform.minimaxi.com/login', timeout=20000)
            page.wait_for_timeout(2000)
            
            page.locator('input[placeholder="请输入手机号/邮箱"]').fill(MINIMAX_EMAIL)
            page.locator('input[placeholder="请输入登录密码"]').fill(MINIMAX_PASSWORD)
            page.locator('input[type="checkbox"]').check()
            page.locator('button:has-text("立即登录")').click()
            page.wait_for_timeout(8000)
            
            cookies = page.context.cookies()
            cookie_str = '; '.join([f"{c['name']}={c['value']}" for c in cookies])
            browser.close()
            return cookie_str
        except Exception as e:
            browser.close()
            return None

def get_usage_from_api(cookie_str):
    """调用 MiniMax API 获取 usage 数据"""
    group_id = "2030122951646389213"
    url = f'https://www.minimaxi.com/v1/api/openplatform/coding_plan/remains?GroupId={group_id}'
    req = urllib.request.Request(url, headers={'Cookie': cookie_str})
    
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())
    
    # 提取 MiniMax-M* 模型数据
    # James确认：current_interval_usage_count = 可用次数，total - usage_count = 已用次数
    for model in data.get('model_remains', []):
        if 'MiniMax-M' in model.get('model_name', ''):
            total = model['current_interval_total_count']
            available = model['current_interval_usage_count']  # API返回=可用次数
            used = total - available  # 已用 = 总量 - 可用
            remains_time_ms = model['remains_time']
            remains_hours = remains_time_ms / 3600000
            available_pct = round(available / total * 100, 1) if total > 0 else 0
            
            return {
                'model': model['model_name'],
                'total': total,
                'available': available,
                'used': used,
                'available_pct': available_pct,
                'remains_hours': round(remains_hours, 1),
            }
    
    return None

def main():
    now = datetime.now(TZ_CST)
    now_str = now.strftime("%m-%d %H:%M")
    
    # 获取 cookies
    cookie_str = get_minimax_cookies()
    if not cookie_str:
        msg = f"📊 MiniMax | {now_str} | ⚠️ 登录失败"
        print(msg)
        with open(LOG_FILE, "a") as f:
            f.write(f"[{now_str}] ERROR: Login failed\n")
        return
    
    # 获取 usage
    usage_data = get_usage_from_api(cookie_str)
    
    if not usage_data:
        msg = f"📊 MiniMax | {now_str} | ⚠️ 无法获取 usage"
        print(msg)
        with open(LOG_FILE, "a") as f:
            f.write(f"[{now_str}] ERROR: No usage data\n")
        return
    
    available = usage_data['available']   # 当前可用次数
    used = usage_data['used']             # 已用次数
    available_pct = usage_data['available_pct']  # 可用比例
    total = usage_data['total']
    remains_hours = usage_data['remains_hours']
    
    # 判断：可用次数 < 5% 总量 时告警
    reduce_mode = available_pct < THRESHOLD_REMAINING_PCT
    
    if reduce_mode:
        emoji = "🔴"
        status = "🔴 REDUCE"
        action = "降低请求频率 | 使用缓存减少重复查询 | 减少调试输出"
    elif available_pct < 10:
        emoji = "🟡"
        status = "🟡 WARNING"
        action = "注意监控，可用即将耗尽"
    else:
        emoji = "🟢"
        status = "✅ NORMAL"
        action = "正常运行"
    
    msg = f"📊 MiniMax | {now_str} | {emoji} 可用: {available}/{total} ({available_pct}%) | {used}已用 | {remains_hours}h | {status}"
    print(msg)
    
    with open(LOG_FILE, "a") as f:
        f.write(f"[{now_str}] Available: {available}/{total} ({available_pct}%) | Used: {used} | {remains_hours}h left | {status}\n")
        if reduce_mode:
            f.write(f"         Actions: {action}\n")
    
    # 触发限流时设置标志文件
    alert_file = Path("/Users/fhjtech/.openclaw/logs/usage_alert.flag")
    if reduce_mode:
        alert_file.write_text(f"{now_str} | Available: {available}/{total} ({available_pct}%)\n")

if __name__ == "__main__":
    main()
