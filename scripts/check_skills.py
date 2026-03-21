#!/usr/bin/env python3
"""
Skills Installation Checker
Check which skills in /Users/fhjtech/.openclaw/workspace/skills are installed
"""

import os
import json
import subprocess
from pathlib import Path

SKILLS_DIR = "/Users/fhjtech/.openclaw/workspace/skills"
OPENCLAW_CONFIG = "/Users/fhjtech/.openclaw/openclaw.json"

# Skills that don't need installation (built-in or special)
BUILTIN_SKILLS = {
    "brainstorming",  # Symlink to .agents/skills
    "find-skills",    # Built-in skill discovery
    "self-improving-agent"  # Already integrated
}

def get_installed_skills():
    """Get list of skills that are actually installed/available to OpenClaw"""
    installed = set()
    
    # Check workspace skills directory
    if os.path.exists(SKILLS_DIR):
        for item in os.listdir(SKILLS_DIR):
            item_path = os.path.join(SKILLS_DIR, item)
            if os.path.isdir(item_path) and not item.startswith('.'):
                # Check if it has SKILL.md or is a valid skill
                if os.path.exists(os.path.join(item_path, "SKILL.md")):
                    installed.add(item)
    
    # Add builtin skills
    installed.update(BUILTIN_SKILLS)
    
    return installed

def check_skill_health(skill_name):
    """Check if a skill is healthy (has SKILL.md and dependencies)"""
    skill_path = os.path.join(SKILLS_DIR, skill_name)
    
    if not os.path.exists(skill_path):
        return {"installed": False, "reason": "Directory not found"}
    
    # Check for SKILL.md
    skill_md = os.path.join(skill_path, "SKILL.md")
    if not os.path.exists(skill_md):
        return {"installed": False, "reason": "No SKILL.md found"}
    
    # Check for required files
    has_readme = os.path.exists(os.path.join(skill_path, "README.md"))
    has_assets = os.path.exists(os.path.join(skill_path, "assets"))
    
    # Check dependencies in SKILL.md
    dependencies = []
    try:
        with open(skill_md, 'r') as f:
            content = f.read()
            if "dependencies:" in content.lower():
                # Extract dependencies
                lines = content.split('\n')
                in_deps = False
                for line in lines:
                    if "dependencies:" in line.lower():
                        in_deps = True
                    elif in_deps and line.strip().startswith('-'):
                        deps = line.strip().lstrip('-').strip()
                        if deps:
                            dependencies.append(deps)
                    elif in_deps and not line.strip().startswith('-'):
                        break
    except:
        pass
    
    return {
        "installed": True,
        "has_readme": has_readme,
        "has_assets": bool(dependencies),
        "dependencies": dependencies,
        "path": skill_path
    }

def analyze_skills():
    """Analyze all skills in the directory"""
    all_skills = []
    
    if not os.path.exists(SKILLS_DIR):
        print(f"❌ Skills directory not found: {SKILLS_DIR}")
        return []
    
    for item in sorted(os.listdir(SKILLS_DIR)):
        item_path = os.path.join(SKILLS_DIR, item)
        
        # Skip hidden files and the nested skills directory
        if item.startswith('.') or item == 'skills' or item == '2':
            continue
        
        if os.path.isdir(item_path):
            # Check if it's a valid skill (has SKILL.md)
            if os.path.exists(os.path.join(item_path, "SKILL.md")):
                health = check_skill_health(item)
                all_skills.append({
                    "name": item,
                    "status": "ready" if health["installed"] else "missing",
                    "details": health
                })
            else:
                # Might be a versioned skill folder
                has_skill_md = False
                for subitem in os.listdir(item_path):
                    if subitem == "SKILL.md":
                        has_skill_md = True
                        break
                
                if has_skill_md:
                    health = check_skill_health(item)
                    all_skills.append({
                        "name": item,
                        "status": "ready",
                        "details": health
                    })
                else:
                    all_skills.append({
                        "name": item,
                        "status": "not_skill",
                        "details": {"reason": "No SKILL.md found"}
                    })
    
    return all_skills

def print_report(skills):
    """Print detailed report"""
    ready = [s for s in skills if s["status"] == "ready"]
    not_skill = [s for s in skills if s["status"] == "not_skill"]
    
    print("\n" + "="*60)
    print("📊 SKILLS INSTALLATION REPORT")
    print("="*60)
    print(f"\n📁 Skills Directory: {SKILLS_DIR}")
    print(f"✅ Ready to use: {len(ready)}")
    print(f"⚠️  Not valid skills: {len(not_skill)}")
    
    if ready:
        print("\n✅ READY SKILLS:")
        for s in ready:
            deps = s["details"].get("dependencies", [])
            dep_str = f" (deps: {', '.join(deps[:3])})" if deps else ""
            print(f"   • {s['name']}{dep_str}")
    
    if not_skill:
        print("\n⚠️  NOT VALID SKILLS (missing SKILL.md):")
        for s in not_skill:
            print(f"   • {s['name']}")
    
    return ready, not_skill

if __name__ == "__main__":
    print("🔍 Checking skills installation...")
    skills = analyze_skills()
    ready, not_skill = print_report(skills)
    
    # Save report
    report = {
        "checked_at": str(Path(__file__).stat().st_mtime) if os.path.exists(__file__) else None,
        "total_checked": len(skills),
        "ready_count": len(ready),
        "ready_skills": [s["name"] for s in ready],
        "not_valid": [s["name"] for s in not_skill]
    }
    
    report_file = "/Users/fhjtech/.openclaw/workspace/.learnings/skills_check_report.json"
    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Report saved to: {report_file}")
