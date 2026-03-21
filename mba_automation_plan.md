# MBA论文修改自动化计划

## 目标
使用agent-browser自动化MBA论文研究的数据收集工作

## 学术网站列表（需要自动化）

### 1. 学术数据库
- Google Scholar (https://scholar.google.com)
- IEEE Xplore (https://ieeexplore.ieee.org)
- ScienceDirect (https://www.sciencedirect.com)
- JSTOR (https://www.jstor.org)

### 2. 企业数据源
- Yahoo Finance (https://finance.yahoo.com)
- Bloomberg (https://www.bloomberg.com)
- 公司官网（如Apple、Tesla等）

### 3. 行业报告
- McKinsey Insights (https://www.mckinsey.com/insights)
- BCG Publications (https://www.bcg.com/publications)
- Deloitte Insights (https://www2.deloitte.com/insights)

## 自动化脚本设计

### 脚本1：学术文献搜索自动化
```bash
#!/bin/bash
# mba_literature_search.sh

# 搜索关键词
KEYWORDS=(
    "MBA curriculum innovation"
    "business education digital transformation"
    "leadership development programs"
    "corporate strategy case studies"
)

for keyword in "${KEYWORDS[@]}"; do
    echo "搜索: $keyword"
    npx agent-browser open "https://scholar.google.com"
    npx agent-browser snapshot -i
    npx agent-browser fill @search "$keyword"
    npx agent-browser click @search_button
    npx agent-browser wait --load networkidle
    npx agent-browser get text @results > "scholar_${keyword// /_}.txt"
    sleep 2
done
```

### 脚本2：企业财务数据收集
```bash
#!/bin/bash
# mba_financial_data.sh

# 公司列表
COMPANIES=(
    "AAPL"  # Apple
    "TSLA"  # Tesla
    "MSFT"  # Microsoft
    "AMZN"  # Amazon
)

for symbol in "${COMPANIES[@]}"; do
    echo "收集 $symbol 财务数据"
    npx agent-browser open "https://finance.yahoo.com/quote/$symbol"
    npx agent-browser wait --load networkidle
    npx agent-browser snapshot -i
    
    # 获取关键财务指标
    npx agent-browser get text @financials > "${symbol}_financials.txt"
    npx agent-browser get text @income_statement > "${symbol}_income.txt"
    npx agent-browser get text @balance_sheet > "${symbol}_balance.txt"
    
    sleep 1
done
```

### 脚本3：行业报告下载
```bash
#!/bin/bash
# mba_industry_reports.sh

REPORT_SITES=(
    "https://www.mckinsey.com/insights"
    "https://www.bcg.com/publications"
    "https://www2.deloitte.com/insights"
)

for site in "${REPORT_SITES[@]}"; do
    domain=$(echo "$site" | awk -F/ '{print $3}')
    echo "访问: $domain"
    
    npx agent-browser open "$site"
    npx agent-browser wait --load networkidle
    npx agent-browser snapshot -i
    
    # 查找最新报告
    npx agent-browser find text "report" click
    npx agent-browser wait --load networkidle
    
    # 获取报告内容
    npx agent-browser get text @content > "${domain}_reports.txt"
    npx agent-browser screenshot "${domain}_screenshot.png"
    
    sleep 2
done
```

## 集成工作流

### 完整的研究流程：
```
1. 文献搜索 → 2. 数据收集 → 3. 报告分析 → 4. 论文整合
```

### 与现有技能集成：
- **search技能**：快速查找资源
- **research技能**：分析合成内容
- **agent-browser技能**：获取原始数据
- **mba技能**：专业框架指导
- **research-paper-writer技能**：写作规范

## 测试计划

### 第一阶段：基本功能测试
1. 测试Google Scholar搜索
2. 测试Yahoo Finance数据获取
3. 测试McKinsey报告访问

### 第二阶段：登录功能测试
1. 测试学术数据库登录（如有权限）
2. 测试付费内容访问

### 第三阶段：批量处理测试
1. 测试多关键词搜索
2. 测试多公司数据收集
3. 测试自动化报告生成

## 风险管理

### 技术风险：
1. 网站反爬虫机制
2. 登录验证码
3. 页面结构变化

### 应对策略：
1. 使用合理的请求间隔
2. 实现错误重试机制
3. 定期更新选择器

## 时间安排

### 第一天：
- 完成Chromium安装
- 测试基本功能
- 设计核心脚本

### 第二天：
- 测试学术网站
- 优化自动化脚本
- 开始数据收集

### 第三天：
- 批量数据收集
- 生成初步分析
- 整合到论文框架