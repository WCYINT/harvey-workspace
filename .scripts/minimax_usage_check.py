#!/usr/bin/env python3
"""
MiniMax API 使用率检查脚本 v11
[DEPRECATED] 此脚本已被 usage_monitor.py (API直调方式) 替代。
请使用: python3 .scripts/usage_monitor.py
本脚本保留仅用于参考，未来将删除。
"""

import json
import os
import sys
from playwright.sync_api import sync_playwright

CHROME_PATH = "/Users/fhjtech/Library/Caches/ms-playwright/chromium-1208/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
MINIMAX_USER = os.environ.get("MINIMAX_USER", "18620362529")
MINIMAX_PASS = os.environ.get("MINIMAX_PASS", "")

def run() -> None:
    # Fallback: 如果环境变量未设置，使用缓存凭证（仅用于开发）
    user = MINIMAX_USER
    password = MINIMAX_PASS or os.environ.get("HARVEY_MINIMAX_PASS", "")
    if not password:
        print("WARNING: MINIMAX_PASS 环境变量未设置，尝试使用缓存凭证", file=sys.stderr)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROME_PATH,
            headless=True
        )
        page = browser.new_page()
        
        # Login
        page.goto("https://platform.minimaxi.com/login")
        page.wait_for_timeout(2000)
        
        page.locator('input[placeholder="请输入手机号/邮箱"]').fill(user)
        page.locator('input[placeholder="请输入登录密码"]').fill(password)
        
        checkbox = page.locator('input[type="checkbox"]')
        if not checkbox.is_checked():
            checkbox.check()
        
        page.locator('button:has-text("立即登录")').click()
        page.wait_for_timeout(5000)
        
        # Go to interface key page
        page.goto("https://platform.minimaxi.com/user-center/basic-information/interface-key")
        page.wait_for_timeout(3000)
        
        # Try clicking "管理订阅计划"
        print("=== Looking for 管理订阅计划 ===")
        page.locator('text=管理订阅计划').click()
        page.wait_for_timeout(5000)
        print(f"URL: {page.url}")
        body_text = page.locator('body').inner_text()
        print(f"Content (first 5000 chars):\n{body_text[:5000]}")
        
        browser.close()

if __name__ == "__main__":
    run()


__all__ = ['run']
