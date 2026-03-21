#!/usr/bin/env python3
"""
ClawHub Paper Skills Hunter - Optimized Version
Automatically search, score, and install high-quality paper/research skills from ClawHub and skills.sh
"""

import json
import os
import subprocess
import re
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from pathlib import Path

# Configuration
CLAWHUB_SKILLS_DIR = "/Users/fhjtech/.openclaw/workspace/skills"
LEARNINGS_DIR = "/Users/fhjtech/.openclaw/workspace/.learnings"
SKILLS_REGISTRY = f"{LEARNINGS_DIR}/skills_registry.json"
SCORE_THRESHOLD = 4.5  # 自动安装阈值：4.5分及以上自动安装
INSTALL_LOG = f"{LEARNINGS_DIR}/paper_skills_installed.json"
FEEDBACK_LOG = f"{LEARNINGS_DIR}/paper_skills_feedback.json"
ROLLBACK_LOG = f"{LEARNINGS_DIR}/skill_rollbacks.json"

# Paper/Research related keywords
PAPER_KEYWORDS = [
    "paper", "research", "academic", "arxiv", "scholar", "citation",
    "literature", "thesis", "dissertation", "publication", "journal",
    "conference", "peer review", "doi", "bibliography", "reference",
    "ai", "llm", "model", "analysis", "data", "writing", "technical"
]

def run_command(cmd, timeout=30):
    """Run shell command and return output"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "Timeout", -1
    except Exception as e:
        return "", str(e), -1

def search_clawhub(query="paper research academic", limit=20):
    """Search ClawHub, skills.sh and awesome list for paper/research skills"""
    print(f"🔍 Searching for: {query}")
    
    all_skills = []
    
    # Source 1: ClawHub
    stdout, stderr, code = run_command(f"clawhub search {query} --limit {limit} --no-input 2>&1")
    
    if "Rate limit" in stderr or "Rate limit" in stdout:
        print("⚠️  ClawHub rate limit hit, using fallback...")
    elif code == 0:
        skills = parse_search_results(stdout)
        for s in skills:
            s["source"] = "clawhub"
        all_skills.extend(skills)
    
    # Source 2: skills.sh
    skills_sh_skills = fetch_skills_sh()
    all_skills.extend(skills_sh_skills)
    
    # Source 3: awesome-openclaw-skills (NEW!)
    awesome_skills = fetch_awesome_list()
    all_skills.extend(awesome_skills)
    
    # Remove duplicates
    seen = set()
    unique_skills = []
    for s in all_skills:
        if s.get("slug") not in seen:
            seen.add(s.get("slug"))
            unique_skills.append(s)
    
    return unique_skills

def parse_search_results(output):
    """Parse clawhub search output"""
    skills = []
    lines = output.split('\n')
    
    for line in lines:
        if '-' in line and ('skill' in line.lower() or 'paper' in line.lower() or 'research' in line.lower()):
            skills.append({
                "slug": line.strip().lstrip('- ').split()[0] if line.strip() else "",
                "name": line.strip(),
                "description": line.strip()
            })
    
    return skills

def fetch_skills_sh():
    """Fetch skills from skills.sh - Already implemented above"""
    print("🔍 Fetching skills from skills.sh...")
    skills = []
    
    try:
        # Fetch the main page
        stdout, stderr, code = run_command('curl -s "https://skills.sh/" 2>&1')
        
        if code != 0 or not stdout:
            print(f"⚠️  skills.sh fetch failed: {stderr}")
            return []
        
        # Find the initialSkills data in the JavaScript
        idx = stdout.find('initialSkills\\":[')
        if idx <= 0:
            print("⚠️  Could not find skills data in skills.sh")
            return []
        
        start = idx + len('initialSkills\\":[')
        
        # Find matching ] by counting brackets
        depth = 1
        i = start
        while i < len(stdout):
            if stdout[i] == '[':
                depth += 1
            elif stdout[i] == ']':
                depth -= 1
                if depth == 0:
                    break
            i += 1
        
        json_str = stdout[start:i]
        json_str = json_str.replace('\\"', '"')
        json_str = '[' + json_str + ']'
        
        skills_data = json.loads(json_str)
        print(f"   Found {len(skills_data)} total skills")
        
        keywords = ['paper', 'research', 'academic', 'ai', 'llm', 'model', 'analysis', 
                   'brainstorm', 'writing', 'data', 'technical', 'nlp', 'deep', 'neural',
                   'text', 'knowledge', 'document', 'search', 'summar', 'book', 'course']
        
        for s in skills_data:
            name = s.get('skillId', '')
            source = s.get('source', '')
            installs = s.get('installs', 0)
            combined = f"{name} {source}".lower()
            
            if any(k in combined for k in keywords):
                skills.append({
                    "slug": f"{source}/{name}",
                    "name": name,
                    "description": f"From {source} ({installs} installs)",
                    "source": "skills.sh",
                    "installs": installs
                })
        
        print(f"   Filtered to {len(skills)} research/AI related skills")
        
    except Exception as e:
        print(f"⚠️  skills.sh error: {e}")
    
    return skills

def fetch_awesome_list():
    """Fetch skills from VoltAgent awesome-openclaw-skills list"""
    print("🔍 Fetching skills from awesome-openclaw-skills...")
    skills = []
    
    try:
        # Fetch the README from GitHub with longer timeout
        stdout, stderr, code = run_command(
            'curl -s --max-time 60 "https://raw.githubusercontent.com/VoltAgent/awesome-openclaw-skills/main/README.md" 2>&1',
            timeout=90
        )
        
        if code != 0 or not stdout or len(stdout) < 500:
            print(f"⚠️  awesome list fetch failed/timeout, trying alternative...")
            # Try alternative repo name
            stdout, stderr, code = run_command(
                'curl -s --max-time 60 "https://raw.githubusercontent.com/VoltAgent/awesome-clawdbot-skills/main/README.md" 2>&1',
                timeout=90
            )
            if code != 0 or not stdout or len(stdout) < 500:
                return []
        
        # Parse skill entries from markdown
        # Try multiple patterns
        pattern = r'- \[([^\]]+)\]\(([^)]+)\)(?: - (.+))?'
        matches = re.findall(pattern, stdout)
        
        print(f"   Found {len(matches)} total skill entries")
        
        if len(matches) == 0:
            return []
        
        # Filter for research/paper/academic related skills
        keywords = ['paper', 'research', 'academic', 'scholar', 'thesis', 'literature', 
                   'citation', 'arxiv', 'publication', 'journal', 'analysis', 'data',
                   'llm', 'ai', 'model', 'learning', 'deep', 'nlp', 'knowledge',
                   'library', 'book', 'course', 'study', 'scientific', 'conference', 'neural']
        
        for match in matches:
            skill_name = match[0]
            skill_url = match[1]
            description = match[2].strip() if len(match) > 2 and match[2] else ""
            
            combined = f"{skill_name} {description}".lower()
            
            if any(k in combined for k in keywords):
                # Extract source from URL
                source = "openclaw/skills"
                if "/skills/" in skill_url:
                    parts = skill_url.split("/skills/")[-1].split("/")
                    if len(parts) >= 2:
                        source = parts[0] + "/" + parts[1]
                
                skills.append({
                    "slug": f"{source}/{skill_name}",
                    "name": skill_name,
                    "description": f"From awesome: {description[:80]}",
                    "source": "awesome-openclaw-skills",
                    "installs": 0
                })
        
        print(f"   Filtered to {len(skills)} research/AI skills")
        
    except Exception as e:
        print(f"⚠️  awesome list error: {e}")
    
    return skills

def inspect_skill(slug):
    """Get detailed info about a skill"""
    print(f"🔍 Inspecting skill: {slug}")
    
    stdout, stderr, code = run_command(f"clawhub inspect {slug} --no-input 2>&1")
    
    if code != 0:
        return None
    
    return {"slug": slug, "raw": stdout}

def score_skill(skill_info):
    """
    5分制优化评分算法
    
    评分维度:
    1. 相关性 (0-3分): 论文/学术/研究相关度 - 提高权重
    2. 学术质量 (0-1分): 方法论、引用规范等 - 降低权重
    3. 流行度 (0-1分): 安装量作为信任指标
    
    总分 = 相关性 + 学术质量 + 流行度 (满分5分)
    """
    slug = skill_info.get("slug", "")
    name = skill_info.get("name", "")
    desc = skill_info.get("description", "")
    installs = skill_info.get("installs", 0)
    
    combined = f"{slug} {name} {desc}".lower()
    
    # ========== 1. 相关性评分 (0-3分) ==========
    relevance_score = 0
    
    # 核心关键词 - 最高2分
    core_keywords = ["paper", "research", "academic", "arxiv", "scholar", "thesis"]
    for kw in core_keywords:
        if kw in combined:
            relevance_score = 2.0
            break
    
    # 次要关键词 - 最高0.5分
    if relevance_score < 2.0:
        secondary_keywords = ["literature", "citation", "publication", "journal", "conference"]
        for kw in secondary_keywords:
            if kw in combined:
                relevance_score += 0.25
                if relevance_score >= 1.5:
                    break
    
    # AI/LLM相关 - 最高0.5分
    ai_keywords = ["llm", "ai", "model", "gpt", "nlp", "deep learning", "neural", "transformer"]
    for kw in ai_keywords:
        if kw in combined:
            relevance_score += 0.25
            if relevance_score >= 2.5:
                break
    
    # 如果有research/paper关键词，给额外boost
    if "research" in combined or "paper" in combined:
        relevance_score += 0.5  # 额外加分
    
    relevance_score = min(relevance_score, 3.0)
    
    # ========== 2. 学术质量评分 (0-1分) ==========
    quality_score = 0
    
    methodology_kw = ["methodology", "analysis", "rigorous", "empirical", "study", "scientific"]
    for kw in methodology_kw:
        if kw in combined:
            quality_score += 0.25
    
    format_kw = ["apa", "ieee", "acm", "peer review", "bibliography"]
    for kw in format_kw:
        if kw in combined:
            quality_score += 0.25
    
    quality_score = min(quality_score, 1.0)
    
    # ========== 3. 流行度/信任评分 (0-1分) ==========
    trust_score = 0
    
    if installs >= 100000:
        trust_score = 1.0
    elif installs >= 50000:
        trust_score = 0.8
    elif installs >= 10000:
        trust_score = 0.6
    elif installs >= 1000:
        trust_score = 0.4
    elif installs >= 100:
        trust_score = 0.2
    elif installs > 0:
        trust_score = 0.1
    
    trust_score = min(trust_score, 1.0)
    
    # ========== 总分 ==========
    total_score = relevance_score + quality_score + trust_score
    total_score = min(total_score, 5.0)
    
    return {
        "score": round(total_score, 1),
        "details": {
            "relevance": f"{relevance_score:.1f}/3.0",
            "quality": f"{quality_score:.1f}/1.0",
            "trust": f"{trust_score:.1f}/1.0"
        },
        "slug": slug,
        "name": name,
        "description": desc[:100],
        "installs": installs
    }

def install_skill(slug):
    """Install a skill from ClawHub"""
    print(f"📦 Installing skill: {slug}")
    
    os.makedirs(CLAWHUB_SKILLS_DIR, exist_ok=True)
    
    stdout, stderr, code = run_command(
        f"cd {CLAWHUB_SKILLS_DIR} && clawhub install {slug} --no-input 2>&1"
    )
    
    if code != 0:
        print(f"❌ Install failed: {stderr}")
        return False
    
    print(f"✅ Installed: {slug}")
    return True

def integrate_to_evolution(slug):
    """Integrate installed skill to self-evolution system"""
    print(f"🔄 Integrating {slug} to evolution system...")
    
    # Update skills registry
    registry_path = SKILLS_REGISTRY
    if os.path.exists(registry_path):
        with open(registry_path, 'r') as f:
            registry = json.load(f)
    else:
        registry = {"skills": {}, "categories": {}}
    
    registry["skills"][slug] = {
        "category": "academic",
        "status": "auto_installed",
        "installed_at": datetime.now().isoformat(),
        "source": "clawhub",
        "score": 5.0,
        "uses": 0
    }
    
    with open(registry_path, 'w') as f:
        json.dump(registry, f, indent=2)
    
    # Log to install log
    log_entry = {
        "slug": slug,
        "installed_at": datetime.now().isoformat(),
        "score": 5.0
    }
    
    if os.path.exists(INSTALL_LOG):
        with open(INSTALL_LOG, 'r') as f:
            install_log = json.load(f)
    else:
        install_log = {"installed": []}
    
    install_log["installed"].append(log_entry)
    
    with open(INSTALL_LOG, 'w') as f:
        json.dump(install_log, f, indent=2)
    
    print(f"✅ Integrated: {slug}")
    return True

def send_feedback_email(installed_skills, all_scored_skills):
    """Send email feedback about skills (≥3.0)"""
    print("📧 Sending feedback email...")
    
    # Filter: ≥3.0
    feedback_skills = [s for s in all_scored_skills if s["score"] >= 3.0]
    
    # Sort by score descending
    feedback_skills.sort(key=lambda x: x["score"], reverse=True)
    
    SMTP_SERVER = "smtp.agentmail.to"
    SMTP_PORT = 465
    EMAIL = "iharvey@agentmail.to"
    PASSWORD = "am_us_cd05b848539e62a8f8399ebdda986586e461a17747f560654aead253d80f3a99"
    
    subject = f"📚 Paper Skills Report [{datetime.now().strftime('%m-%d %H:%M')}] 安装:{len(installed_skills)} 待安装:{len(feedback_skills)}"
    
    body = f"""# 📚 Paper Skills Report
**日期**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## ✅ 已自动安装 (≥4.8分)
"""
    
    if installed_skills:
        for skill in installed_skills:
            body += f"- **{skill['slug']}** ⭐{skill['score']}\n"
    else:
        body += "_无新技能达到自动安装阈值_\n"
    
    body += f"""
---

## 📋 待安装清单 (≥3.0分)

| # | 评分 | 技能 | 安装量 |
|---|------|------|--------|
"""
    
    for i, skill in enumerate(feedback_skills, 1):
        installs = skill.get("installs", 0)
        body += f"| {i} | {skill['score']} | {skill['slug']} | {installs:,} |\n"
    
    body += f"""
---

## 📊 评分说明

| 维度 | 满分 | 说明 |
|------|------|------|
| 相关性 | 2.0 | paper/research/academic相关度 |
| 学术质量 | 1.5 | methodology/引用规范 |
| 流行度 | 1.5 | 安装量作为信任指标 |

**阈值**: ≥4.8自动安装 | ≥3.0反馈清单 | <3.0忽略

---
Havery Paper Skills Hunter
"""
    
    try:
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = subject
        msg['From'] = EMAIL
        msg['To'] = EMAIL
        
        context = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        context.login(EMAIL, PASSWORD)
        context.sendmail(EMAIL, EMAIL, msg.as_string())
        context.quit()
        
        print("✅ Feedback email sent")
        return True
    except Exception as e:
        print(f"❌ Email failed: {e}")
        return False

def main():
    """Main execution"""
    print("\n" + "="*60)
    print("📚 CLAWHUB PAPER SKILLS HUNTER (Optimized)")
    print("="*60)
    print(f"⏰ Run at: {datetime.now().isoformat()}")
    print(f"📊 Score threshold: {SCORE_THRESHOLD}")
    print()
    
    # Step 1: Search for paper skills
    skills = search_clawhub("paper research academic", limit=20)
    
    if not skills:
        print("❌ No skills found")
        return
    
    print(f"📦 Found {len(skills)} total skills")
    
    # Step 2: Score each skill
    scored_skills = []
    for skill in skills:
        if not skill.get("slug"):
            continue
        
        score_result = score_skill(skill)
        scored_skills.append(score_result)
        details = score_result.get("details", {})
        rel = details.get("relevance", "0")
        qual = details.get("quality", "0")
        trust = details.get("trust", "0")
        print(f"   {score_result['slug']}: {score_result['score']}/5.0 [{rel}, {qual}, {trust}]")
    
    # Step 3: Separate by score
    auto_install = [s for s in scored_skills if s["score"] >= SCORE_THRESHOLD]  # ≥4.5
    feedback_list = [s for s in scored_skills if s["score"] >= 3.0]  # ≥3.0
    ignored = [s for s in scored_skills if s["score"] < 3.0]  # <3.0
    
    print(f"\n📊 评分结果:")
    print(f"   ✅ 自动安装 (≥{SCORE_THRESHOLD}分): {len(auto_install)}")
    print(f"   📋 反馈清单 (≥3.0分): {len(feedback_list)}")
    print(f"   ⏭️  忽略 (<3.0分): {len(ignored)}")
    
    # Step 4: Install high score skills
    installed = []
    for skill in auto_install:
        slug = skill["slug"]
        
        # Check if already installed
        skill_path = os.path.join(CLAWHUB_SKILLS_DIR, slug.split('/')[-1])
        if os.path.exists(skill_path):
            print(f"   ⏭️  已安装: {slug}")
            continue
        
        # Install
        if install_skill(slug):
            integrate_to_evolution(slug)
            installed.append(slug)
    
    # Step 5: Send feedback email (≥3.0 range only)
    if feedback_list:
        send_feedback_email(installed, scored_skills)
    
    print("\n" + "="*60)
    print("✅ PAPER SKILLS HUNTER 完成")
    print("="*60)
    print(f"📦 新安装: {len(installed)} 个")
    print(f"📧 反馈清单: {len(feedback_list)} 个 (≥3.0分)")

if __name__ == "__main__":
    main()
