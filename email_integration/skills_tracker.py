#!/usr/bin/env python3
"""
Skills Usage Tracker
Integrates with self-improving-agent to track skill usage patterns
"""

import json
import os
from datetime import datetime
from pathlib import Path

TRACKING_FILE = "/Users/fhjtech/.openclaw/workspace/.learnings/skills_usage.json"

# Skill usage categories
SKILL_CATEGORIES = {
    "academic": ["academic-deep-research", "academic-research", "academic-writing", 
                 "arxiv-1", "paper-parse", "paper-recommendation", "research-paper-writer",
                 "mba-thesis", "mba"],
    "business": ["business-writing", "data-analysis", "decision-trees", 
                 "market-research", "resume-builder"],
    "search": ["exa-plus", "exaaa-web-search-free", "deepwiki", "miniflux-news", 
               "technews", "tavily-search", "get-tldr"],
    "dev": ["github", "pdf-extract", "pdf-to-structured", "md2pdf-weasyprint",
            "agent-browser", "humanizer-zh"],
    "productivity": ["personal-assistant", "brainstorming", "find-skills", "free-ride-1"],
    "improvement": ["self-improving-agent", "evolver", "openclaw-agent-optimize", "rollback-manager"]
}

def record_skill_usage(skill_name: str, context: str = ""):
    """Record skill usage for learning"""
    data = load_usage_data()
    
    if skill_name not in data["skills"]:
        data["skills"][skill_name] = {"count": 0, "first_used": None, "contexts": []}
    
    data["skills"][skill_name]["count"] += 1
    data["skills"][skill_name]["last_used"] = datetime.now().isoformat()
    
    if not data["skills"][skill_name]["first_used"]:
        data["skills"][skill_name]["first_used"] = datetime.now().isoformat()
    
    if context:
        data["skills"][skill_name]["contexts"].append(context)
    
    # Track category usage
    for category, skills in SKILL_CATEGORIES.items():
        if skill_name in skills:
            data["categories"][category] = data["categories"].get(category, 0) + 1
    
    data["total_uses"] += 1
    data["last_update"] = datetime.now().isoformat()
    
    save_usage_data(data)
    return data

def load_usage_data() -> dict:
    """Load usage data from file"""
    if os.path.exists(TRACKING_FILE):
        with open(TRACKING_FILE, 'r') as f:
            return json.load(f)
    return {
        "skills": {},
        "categories": {},
        "total_uses": 0,
        "last_update": None
    }

def save_usage_data(data: dict):
    """Save usage data to file"""
    os.makedirs(os.path.dirname(TRACKING_FILE), exist_ok=True)
    with open(TRACKING_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_skill_stats() -> dict:
    """Get skill usage statistics"""
    return load_usage_data()

def get_top_skills(limit: int = 10) -> list:
    """Get top N most used skills"""
    data = load_usage_data()
    skills = data.get("skills", {})
    sorted_skills = sorted(skills.items(), key=lambda x: x[1].get("count", 0), reverse=True)
    return sorted_skills[:limit]

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        skill = sys.argv[1]
        context = sys.argv[2] if len(sys.argv) > 2 else ""
        record_skill_usage(skill, context)
        print(f"Recorded usage: {skill}")
    else:
        print("Skills Usage Statistics:")
        print(json.dumps(get_skill_stats(), indent=2))
