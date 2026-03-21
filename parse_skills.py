import re
import subprocess

def extract_section(content, section_title):
    # 查找指定标题的部分
    pattern = r'<details open>\s*<summary><h3 style="display:inline">' + re.escape(section_title) + r'</h3></summary>(.*?)</details>'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        # 尝试其他可能的模式
        pattern2 = r'<details>\s*<summary><h3 style="display:inline">' + re.escape(section_title) + r'</h3></summary>(.*?)</details>'
        match = re.search(pattern2, content, re.DOTALL)
    
    if match:
        section_content = match.group(1)
        # 提取技能链接
        skills = re.findall(r'- \[(.*?)\]\((.*?)\) - (.*?)(?=\n- \[|\n$|\Z)', section_content, re.DOTALL)
        return skills
    return []

def main():
    # 下载README内容
    print("Downloading README...")
    result = subprocess.run(
        ["curl", "-s", "https://raw.githubusercontent.com/Anyjames/awesome-openclaw-skills/main/README.md"],
        capture_output=True,
        text=True
    )
    
    content = result.stdout
    
    # 提取Marketing & Sales部分
    print("\n=== MARKETING & SALES SKILLS (94 skills) ===")
    marketing_skills = extract_section(content, "Marketing & Sales")
    
    # 筛选对MBA论文有帮助的技能
    mba_keywords = ['research', 'data', 'analysis', 'market', 'business', 'survey', 'statistic', 'report', 'presentation', 'strategy', 'competitor', 'customer', 'financial', 'economic']
    
    mba_relevant = []
    for name, url, desc in marketing_skills:
        desc_lower = desc.lower()
        name_lower = name.lower()
        
        # 检查是否包含MBA相关关键词
        for keyword in mba_keywords:
            if keyword in desc_lower or keyword in name_lower:
                mba_relevant.append((name, url, desc))
                break
    
    print(f"\nFound {len(mba_relevant)} Marketing & Sales skills relevant for MBA thesis:")
    for i, (name, url, desc) in enumerate(mba_relevant, 1):
        print(f"{i}. {name}: {desc[:120]}...")
    
    # 提取Data & Analytics部分
    print("\n\n=== DATA & ANALYTICS SKILLS (18 skills) ===")
    data_skills = extract_section(content, "Data & Analytics")
    
    data_relevant = []
    for name, url, desc in data_skills:
        desc_lower = desc.lower()
        name_lower = name.lower()
        
        for keyword in ['data', 'analysis', 'statistic', 'visual', 'chart', 'graph', 'excel', 'spreadsheet', 'survey']:
            if keyword in desc_lower or keyword in name_lower:
                data_relevant.append((name, url, desc))
                break
    
    print(f"\nFound {len(data_relevant)} Data & Analytics skills relevant for MBA thesis:")
    for i, (name, url, desc) in enumerate(data_relevant, 1):
        print(f"{i}. {name}: {desc[:120]}...")
    
    # 提取Search & Research部分
    print("\n\n=== SEARCH & RESEARCH SKILLS (148 skills) ===")
    research_skills = extract_section(content, "Search & Research")
    
    research_relevant = []
    for name, url, desc in research_skills:
        desc_lower = desc.lower()
        name_lower = name.lower()
        
        for keyword in ['research', 'search', 'academic', 'paper', 'literature', 'journal', 'article', 'citation', 'reference']:
            if keyword in desc_lower or keyword in name_lower:
                research_relevant.append((name, url, desc))
                break
    
    print(f"\nFound {len(research_relevant)} Search & Research skills relevant for MBA thesis:")
    for i, (name, url, desc) in enumerate(research_relevant[:15], 1):
        print(f"{i}. {name}: {desc[:120]}...")
    
    # 建议安装的技能
    print("\n\n=== RECOMMENDED SKILLS TO INSTALL ===")
    recommended = []
    
    # 从相关技能中选择
    all_relevant = mba_relevant + data_relevant + research_relevant
    
    # 去重
    unique_skills = {}
    for name, url, desc in all_relevant:
        if name not in unique_skills:
            unique_skills[name] = (name, url, desc)
    
    # 选择最相关的
    priority_skills = []
    for name, url, desc in unique_skills.values():
        desc_lower = desc.lower()
        # 高优先级关键词
        high_priority_keywords = ['research', 'data analysis', 'market analysis', 'statistic', 'survey', 'academic', 'literature']
        for keyword in high_priority_keywords:
            if keyword in desc_lower:
                priority_skills.append((name, url, desc))
                break
    
    print(f"\nTop {len(priority_skills)} recommended skills for MBA thesis work:")
    for i, (name, url, desc) in enumerate(priority_skills, 1):
        print(f"{i}. {name}: {desc[:100]}...")
        print(f"   Install: npx clawhub@latest install {name}")
    
    return priority_skills

if __name__ == "__main__":
    main()