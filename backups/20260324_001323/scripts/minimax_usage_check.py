#!/usr/bin/env python3
"""
MiniMax API 使用率检查脚本 v11
查找订阅使用量
"""

import json
from playwright.sync_api import sync_playwright

CHROME_PATH = "/Users/fhjtech/Library/Caches/ms-playwright/chromium-1208/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"

def run() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROME_PATH,
            headless=True
        )
        page = browser.new_page()
        
        # Login
        page.goto("https://platform.minimaxi.com/login")
        page.wait_for_timeout(2000)
        
        page.locator('input[placeholder="请输入手机号/邮箱"]').fill("18620362529")
        page.locator('input[placeholder="请输入登录密码"]').fill("WG17sjjlove")
        
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
