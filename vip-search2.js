const { chromium } = require('playwright');

async function searchVIP(keyword) {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  try {
    console.log(`\n=== 搜索: ${keyword} ===`);
    
    // 1. 访问维普首页
    await page.goto('https://www.cqvip.com/', { timeout: 30000 });
    await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});
    await page.waitForTimeout(2000);
    
    // 2. 找到搜索框 - 根据页面结构选择器
    // 尝试多种可能的搜索框选择器
    const searchSelectors = [
      'input[placeholder*="搜索"]',
      'input[name="keywords"]',
      'input.search-input',
      '#keyword',
      'input[type="text"]'
    ];
    
    let searchBox = null;
    for (const selector of searchSelectors) {
      searchBox = page.locator(selector).first();
      if (await searchBox.isVisible({ timeout: 2000 }).catch(() => false)) {
        console.log('找到搜索框:', selector);
        break;
      }
    }
    
    if (!searchBox || !await searchBox.isVisible({ timeout: 2000 }).catch(() => false)) {
      console.log('未找到搜索框，尝试点击搜索图标...');
      // 点击搜索图标
      const searchIcon = page.locator('.icon-search, .search-icon, [class*="search"]').first();
      if (await searchIcon.isVisible({ timeout: 2000 }).catch(() => false)) {
        await searchIcon.click();
        await page.waitForTimeout(1000);
      }
    }
    
    // 3. 输入关键词
    await searchBox.fill(keyword);
    console.log('已输入关键词:', keyword);
    
    // 4. 点击搜索按钮
    const searchBtn = page.getByRole('button', { name: /搜索|查询/i }).first();
    if (await searchBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
      await searchBtn.click();
    } else {
      // 尝试按回车
      await searchBox.press('Enter');
    }
    
    // 5. 等待结果
    await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});
    await page.waitForTimeout(3000);
    
    // 6. 获取结果数量
    const pageText = await page.locator('body').textContent();
    
    // 尝试多种结果选择器
    const resultCountSelectors = [
      '.result-count',
      '.total',
      '[class*="count"]',
      '[class*="result"]'
    ];
    
    let resultCount = '未找到';
    for (const selector of resultCountSelectors) {
      const element = page.locator(selector).first();
      if (await element.isVisible({ timeout: 1000 }).catch(() => false)) {
        const text = await element.textContent();
        if (text && text.match(/\d+/)) {
          resultCount = text;
          break;
        }
      }
    }
    
    console.log('页面文本前500字符:', pageText.substring(0, 500));
    console.log('估计结果数:', resultCount);
    
    // 7. 截图
    await page.screenshot({ path: `vip-result-${keyword}.png`, fullPage: true });
    console.log('截图已保存');
    
  } catch (error) {
    console.error('错误:', error.message);
    await page.screenshot({ path: `vip-error-${keyword}.png` });
  } finally {
    await browser.close();
  }
}

const keyword = process.argv[2] || 'PDCA 质量管理';
searchVIP(keyword);
