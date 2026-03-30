#!/usr/bin/env python3
"""
LaunchAgents 备份脚本
每天自动备份 Harvey 相关的 LaunchAgents plist 文件到 backups 目录
"""

import shutil
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

TZ_CST = timezone(timedelta(hours=8))

BACKUP_DIR = Path("/Users/fhjtech/.openclaw/workspace/backups/launchagents")
SOURCE_DIR = Path("/Users/fhjtech/Library/LaunchAgents")

# Harvey 相关 LaunchAgents
HARVEY_AGENTS = [
    "com.hjtech.daily-summary.plist",
    "com.hjtech.skill-discovery.plist",
    "com.hjtech.auto-learner.plist",
    "com.hjtech.usage-monitor.plist",
    "ai.openclaw.email-integration.plist",
    "ai.openclaw.gateway.plist",
    "com.fhjtech.evomap.heartbeat.plist",
]

BACKUP_METADATA = Path("/Users/fhjtech/.openclaw/workspace/.learnings/launchagent_backups.json")

def backup_launchagents() -> None:
    """备份 Harvey 相关的 LaunchAgents"""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    today = datetime.now(TZ_CST).strftime("%Y-%m-%d")
    timestamp = datetime.now(TZ_CST).strftime("%Y%m%d_%H%M%S")
    
    backed_up = []
    for plist_name in HARVEY_AGENTS:
        src = SOURCE_DIR / plist_name
        if src.exists():
            dst = BACKUP_DIR / f"{timestamp}_{plist_name}"
            shutil.copy2(src, dst)
            backed_up.append({
                "name": plist_name,
                "backup_path": str(dst),
                "backup_time": datetime.now(TZ_CST).isoformat(),
                "size": dst.stat().st_size
            })
    
    # 更新备份记录
    try:
        with open(BACKUP_METADATA, "r") as f:
            metadata = json.load(f)
    except:
        metadata = {"backups": []}
    
    metadata["backups"].append({
        "date": today,
        "timestamp": timestamp,
        "files": backed_up
    })
    
    # 只保留最近 30 天的备份记录
    cutoff = datetime.now(TZ_CST) - timedelta(days=30)
    metadata["backups"] = [
        b for b in metadata["backups"]
        if datetime.fromisoformat(b["timestamp"]).replace(tzinfo=TZ_CST) > cutoff
    ]
    
    with open(BACKUP_METADATA, "w") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"[Backup] 备份了 {len(backed_up)} 个 LaunchAgent 文件")
    return backed_up

def restore_latest() -> None:
    """恢复最新的备份"""
    try:
        with open(BACKUP_METADATA, "r") as f:
            metadata = json.load(f)
    except:
        print("[Restore] 无备份记录")
        return
    
    if not metadata.get("backups"):
        print("[Restore] 无备份记录")
        return
    
    latest = metadata["backups"][-1]
    restored = []
    for file_info in latest["files"]:
        src = Path(file_info["backup_path"])
        dst = SOURCE_DIR / file_info["name"]
        if src.exists():
            shutil.copy2(src, dst)
            restored.append(file_info["name"])
    
    print(f"[Restore] 恢复了 {len(restored)} 个文件: {restored}")
    return restored

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--restore":
        restore_latest()
    else:
        backup_launchagents()


__all__ = ['backup_launchagents', 'restore_latest']
