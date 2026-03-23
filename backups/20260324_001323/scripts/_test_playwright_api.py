#!/usr/bin/env python3
"""Test playwright MiniMax API call"""
import json
import urllib.request
from playwright.sync_api import sync_playwright

CHROME_PATH = "/Users/fhjtech/Library/Caches/ms-playwright/chromium-1208/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=CHROME_PATH, headless=True)
    page = browser.new_page()
    page.goto('https://platform.minimaxi.com/login')
    page.wait_for_timeout(2000)
    page.locator('input[placeholder="请输入手机号/邮箱"]').fill('18620362529')
    page.locator('input[placeholder="请输入登录密码"]').fill('WG17sjjlove')
    page.locator('input[type="checkbox"]').check()
    page.locator('button:has-text("立即登录")').click()
    page.wait_for_timeout(6000)
    
    cookies = page.context.cookies()
    cookie_str = '; '.join([f"{c['name']}={c['value']}" for c in cookies])
    
    url = 'https://www.minimaxi.com/v1/api/openplatform/coding_plan/remains'
    req = urllib.request.Request(url, headers={'Cookie': cookie_str, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
    
    for model in data.get('model_remains', []):
        name = model['model_name']
        if 'MiniMax-M' in name:
            result = {
                'interval_used': model['current_interval_usage_count'],
                'interval_total': model['current_interval_total_count'],
                'remains_time': model['remains_time']
            }
            print(json.dumps(result))
            break
    browser.close()
