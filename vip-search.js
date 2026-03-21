const { chromium } = require('playwright');

async function searchVIP(keyword) {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  try {
    console.log(`搜索: ${keyword}`);
    
    // 1. 访问深圳图书馆数字资源
    await page.goto('https://er.szlib.org.cn:8899/https/vpn/4/P75YPLUDN3WXTLUPMW4A/', { timeout: 30000 });
    await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});
    
    // 2. 寻找维普入口并点击
    const vipLinks = await page.getByText('维普').all();
    if (vipLinks.length > 0) {
      await vipLinks[0].click();
      await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});
    }
    
    // 3. 尝试直接访问维普
    await page.goto('http://qikan.cqvip.com/', { timeout: 30000 });
    await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});
    
    // 4. 查找搜索框并输入关键词
    const searchBox = page.locator('input[placeholder*="搜索"], input[name*="keyword"], input[name*="search"]').first();
    if (await searchBox.isVisible({ timeout: 5000 }).catch(() => false)) {
      await searchBox.fill(keyword);
      
      // 5. 点击搜索按钮
      const searchBtn = page.getByRole('button', { name: /搜索|查询/i }).first();
      if (await searchBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
        await searchBtn.click();
        await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});
      }
    }
    
    // 6. 获取页面内容
    const content = await page.content();
    const title = await page.title();
    
    console.log(`页面标题: ${title}`);
    console.log(`页面内容长度: ${content.length} 字符`);
    
    // 7. 保存截图
    await page.screenshot({ path: `vip-search-${keyword}.png`, fullPage: true });
    console.log(`截图已保存: vip-search-${keyword}.png`);
    
  } catch (error) {
    console.error(`错误: ${error.message}`);
    await page.screenshot({ path: `vip-error-${keyword}.png` });
  } finally {
    await browser.close();
  }
}

const keyword = process.argv[2] || 'PDCA 质量管理';
searchVIP(keyword);
