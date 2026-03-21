#!/usr/bin/env python3
"""
SkillHub 技能自动更新脚本
每3小时执行一次，自动检查、安装、测试新技能
"""

import subprocess
import json
from datetime import datetime
from pathlib import Path

SKILLS_DIR = Path("/Users/fhjtech/.openclaw/workspace/skills")
SKILLS_DB = Path("/Users/fhjtech/.openclaw/workspace/.learnings/skills_usage.json")
LOG_FILE = Path("/Users/fhjtech/.openclaw/workspace/.learnings/skill_updates.log")
SKILLHUB_CMD = "/Users/fhjtech/.local/bin/skillhub"

def log(msg):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {msg}"
    print(entry)
    with open(LOG_FILE, 'a') as f:
        f.write(entry + "\n")

def get_installed_skills():
    """获取已安装技能列表"""
    if not SKILLS_DIR.exists():
        return set()
    return {d.name for d in SKILLS_DIR.iterdir() if d.is_dir()}

def get_skillhub_top_skills(category=None, limit=100):
    """从SkillHub获取热门技能"""
    try:
        # 使用skillhub explore获取技能列表
        result = subprocess.run(
            [SKILLHUB_CMD, "explore"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return result.stdout
    except Exception as e:
        log(f"Error fetching SkillHub: {e}")
    return ""

def check_and_install_missing():
    """检查并安装缺失的技能"""
    installed = get_installed_skills()
    log(f"Currently installed: {len(installed)} skills")
    
    # 热门技能关键词（按类别）
    categories = ["research", "academic", "writing", "coding", "browser", "memory", "email"]
    new_installs = []
    
    for cat in categories:
        try:
            result = subprocess.run(
                [SKILLHUB_CMD, "search", cat],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                lines = result.stdout.split("\n")
                for line in lines:
                    if line.strip() and ":" in line:
                        skill_name = line.split(":")[0].strip()
                        if skill_name and skill_name not in installed:
                            install_result = subprocess.run(
                                [SKILLHUB_CMD, "install", skill_name],
                                capture_output=True, text=True, timeout=60
                            )
                            if install_result.returncode == 0:
                                new_installs.append(skill_name)
                                installed.add(skill_name)
                                log(f"Installed: {skill_name}")
        except Exception as e:
            log(f"Error searching {cat}: {e}")
    
    return new_installs

def update_skills_db(new_skills):
    """更新技能数据库"""
    if not new_skills:
        return
    
    try:
        with open(SKILLS_DB, 'r') as f:
            data = json.load(f)
    except:
        data = {"skills": {}, "categories": {}, "total_uses": 0}
    
    for skill in new_skills:
        if skill not in data["skills"]:
            data["skills"][skill] = {
                "count": 0,
                "first_used": None,
                "contexts": [],
                "last_used": None,
                "description": f"Auto-installed on {datetime.now().date()}",
                "status": "auto-installed"
            }
    
    data["last_update"] = datetime.now().isoformat()
    
    with open(SKILLS_DB, 'w') as f:
        json.dump(data, f, indent=2)
    
    log(f"Updated skills DB with {len(new_skills)} new skills")

def main():
    log("=== Starting SkillHub Auto-Update ===")
    new = check_and_install_missing()
    if new:
        update_skills_db(new)
        log(f"=== Completed: Installed {len(new)} new skills ===")
    else:
        log("=== Completed: No new skills needed ===")

if __name__ == "__main__":
    main()
