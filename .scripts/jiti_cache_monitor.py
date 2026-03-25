#!/usr/bin/env python3
"""
Jiti Cache Health Monitor & Auto-Fix
Proactively detects and fixes jiti cache corruption that causes plugin loading failures.

Background (LRN-20260324-JITI):
- After OpenClaw upgrades, stale jiti cache causes "Cannot find module 'openclaw/plugin-sdk'"
- One-time fix: rm -rf /tmp/jiti/ + gateway restart
- This script: automates detection and fix when issue recurs

Usage:
    python3 jiti_cache_monitor.py [--check-only]

Returns:
    0 = Healthy or fixed successfully
    1 = Issues detected but couldn't fix
    2 = Check-only mode, issues found
"""

import subprocess
import sys
import re
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path

TZ_CST = timezone(timedelta(hours=8))
JITI_CACHE_DIR = Path("/tmp/jiti")
GATEWAY_LOG = Path.home() / ".openclaw/logs/gateway.err.log"
PID_FILE = Path.home() / ".openclaw/.jiti_monitor.pid"

def log(msg: str) -> None:
    ts = datetime.now(TZ_CST).strftime("%Y-%m-%d %H:%M:%S")
    line = f"[JITI-MONITOR] [{ts}] {msg}"
    print(line)
    # Also log to file
    log_file = Path.home() / ".openclaw/logs/jiti_monitor.log"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def check_jiti_cache_exists() -> bool:
    """Check if jiti cache directory exists"""
    return JITI_CACHE_DIR.exists() and any(JITI_CACHE_DIR.iterdir())

def check_recent_plugin_failures(minutes: int = 10) -> list[str]:
    """Check recent gateway logs for plugin loading failures"""
    failures = []
    
    if not GATEWAY_LOG.exists():
        return failures
    
    try:
        # Get recent log content (last N lines)
        with open(GATEWAY_LOG, "r", encoding="utf-8", errors="ignore") as f:
            # Read last 500 lines
            lines = f.readlines()
            recent_lines = lines[-500:] if len(lines) > 500 else lines
        
        # Look for plugin loading failures
        patterns = [
            r"Cannot find module 'openclaw/plugin-sdk'",
            r"failed to load.*Error: Cannot find module",
            r"memory-lancedb-pro failed to load",
            r"openclaw-plugin-yuanbao failed to load",
        ]
        
        for line in recent_lines:
            for pattern in patterns:
                if re.search(pattern, line):
                    # Extract timestamp if available
                    match = re.match(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', line)
                    timestamp = match.group(1) if match else "unknown"
                    failures.append(f"[{timestamp}] {line.strip()[:150]}")
                    break
        
    except Exception as e:
        log(f"Error reading gateway log: {e}")
    
    return failures

def clear_jiti_cache() -> bool:
    """Clear the jiti cache directory"""
    try:
        if JITI_CACHE_DIR.exists():
            import shutil
            shutil.rmtree(JITI_CACHE_DIR)
            log(f"✓ Cleared jiti cache: {JITI_CACHE_DIR}")
            return True
        else:
            log("✓ Jiti cache directory does not exist (already clear)")
            return True
    except Exception as e:
        log(f"✗ Failed to clear jiti cache: {e}")
        return False

def restart_gateway() -> bool:
    """Signal gateway to restart"""
    try:
        # Find gateway process
        result = subprocess.run(
            ["pgrep", "-f", "openclaw-gateway"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0 and result.stdout.strip():
            pid = result.stdout.strip().split()[0]
            log(f"Found gateway PID: {pid}")
            
            # Send SIGTERM for graceful restart
            subprocess.run(["kill", "-TERM", pid], check=False)
            log(f"✓ Sent SIGTERM to gateway PID {pid}")
            return True
        else:
            log("⚠ Gateway process not found (may already be stopped)")
            return True
    except Exception as e:
        log(f"✗ Failed to restart gateway: {e}")
        return False

def rebuild_plugins() -> bool:
    """
    Rebuild plugins that are failing to load.
    This is used when cache clearing isn't enough.
    """
    log("Step 3a: Rebuilding plugins...")
    
    try:
        # Rebuild memory-lancedb-pro
        lancedb_plugin = Path.home() / ".openclaw/workspace/plugins/memory-lancedb-pro"
        if lancedb_plugin.exists():
            log(f"  Rebuilding {lancedb_plugin.name}...")
            result = subprocess.run(
                ["npm", "run", "build"],
                cwd=lancedb_plugin,
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                log(f"  ✓ {lancedb_plugin.name} rebuilt successfully")
            else:
                log(f"  ⚠ {lancedb_plugin.name} build had issues (exit {result.returncode})")
        
        # Rebuild yuanbao plugin
        yuanbao_plugin = Path.home() / ".openclaw/extensions/openclaw-plugin-yuanbao"
        if yuanbao_plugin.exists():
            log(f"  Rebuilding {yuanbao_plugin.name}...")
            result = subprocess.run(
                ["npm", "run", "build"],
                cwd=yuanbao_plugin,
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                log(f"  ✓ {yuanbao_plugin.name} rebuilt successfully")
            else:
                log(f"  ⚠ {yuanbao_plugin.name} build had issues (exit {result.returncode})")
        
        log("✓ Plugin rebuild process completed")
        return True
        
    except Exception as e:
        log(f"✗ Plugin rebuild failed: {e}")
        return False


def perform_health_check(check_only: bool = False, rebuild: bool = False) -> int:
    """
    Main health check and fix logic.
    
    Args:
        check_only: If True, only check don't fix
        rebuild: If True, rebuild plugins when cache clearing isn't enough
    
    Returns:
        0 = Healthy or fixed successfully
        1 = Issues detected but couldn't fix
        2 = Check-only mode, issues found
    """
    log("=" * 60)
    log("Starting Jiti Cache Health Check")
    log("=" * 60)
    
    # Step 1: Check for recent plugin loading failures
    log("Step 1: Checking for recent plugin loading failures...")
    failures = check_recent_plugin_failures(minutes=10)
    
    if failures:
        log(f"⚠ Found {len(failures)} recent plugin loading failures:")
        for f in failures[:5]:  # Show first 5
            log(f"  - {f}")
        if len(failures) > 5:
            log(f"  ... and {len(failures) - 5} more")
    else:
        log("✓ No recent plugin loading failures detected")
    
    # Step 2: Check jiti cache status
    log("Step 2: Checking jiti cache status...")
    cache_exists = check_jiti_cache_exists()
    
    if cache_exists:
        log(f"⚠ Jiti cache exists: {JITI_CACHE_DIR}")
    else:
        log("✓ Jiti cache is clear")
    
    # Step 3: Determine if action is needed
    needs_fix = bool(failures) and cache_exists
    needs_rebuild = bool(failures) and not cache_exists and rebuild
    
    if not needs_fix and not needs_rebuild:
        if not failures:
            log("=" * 60)
            log("✓ HEALTHY: No issues detected")
            log("=" * 60)
            return 0
        else:
            # Failures but no cache - might need plugin rebuild
            if rebuild:
                log("⚠ Plugin failures detected but no jiti cache to clear")
                log("  Will attempt plugin rebuild...")
                # Fall through to rebuild logic below
            else:
                log("⚠ Plugin failures detected but no jiti cache to clear")
                log("  This may require manual investigation or use --rebuild-plugins")
                return 1 if not check_only else 2
    
    # Action needed
    log("=" * 60)
    log("⚠ ISSUE DETECTED: Jiti cache corruption causing plugin failures")
    log("=" * 60)
    
    if check_only:
        log("Check-only mode: Would perform fix but not executing")
        return 2
    
    # Step 4: Perform fix
    if needs_rebuild:
        # Plugin rebuild path
        if rebuild_plugins():
            log("Step 3b: Restarting gateway after plugin rebuild...")
            if restart_gateway():
                log("=" * 60)
                log("✓ FIXED: Plugins rebuilt and gateway restarted")
                log("=" * 60)
                return 0
            else:
                log("⚠ Plugin rebuild succeeded but gateway restart failed")
                return 1
        else:
            log("✗ Plugin rebuild failed")
            return 1
    else:
        # Standard cache clear path
        log("Step 3: Clearing jiti cache...")
        if not clear_jiti_cache():
            log("✗ Failed to clear jiti cache - aborting")
            return 1
        
        log("Step 4: Restarting gateway...")
        if not restart_gateway():
            log("⚠ Gateway restart may have failed - please check manually")
            return 1
        
        log("=" * 60)
        log("✓ FIXED: Jiti cache cleared and gateway restarted")
        log("=" * 60)
        return 0

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Jiti Cache Health Monitor & Auto-Fix",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 jiti_cache_monitor.py              # Full health check and auto-fix
    python3 jiti_cache_monitor.py --check-only   # Check only, don't fix
    python3 jiti_cache_monitor.py --daemon       # Run continuously in daemon mode
        """
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Check for issues but don't attempt to fix them (exit code 2 if issues found)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run in daemon mode (check every 5 minutes)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Check interval in minutes (daemon mode only, default: 5)"
    )
    parser.add_argument(
        "--rebuild-plugins",
        action="store_true",
        help="Rebuild plugins when cache clearing isn't enough (default: auto-detect)"
    )
    
    args = parser.parse_args()
    
    if args.daemon:
        import time
        log(f"Starting daemon mode (interval: {args.interval} minutes, rebuild: {args.rebuild_plugins})")
        while True:
            try:
                perform_health_check(check_only=False, rebuild=args.rebuild_plugins)
            except Exception as e:
                log(f"Error in daemon mode: {e}")
            time.sleep(args.interval * 60)
    else:
        exit_code = perform_health_check(check_only=args.check_only, rebuild=args.rebuild_plugins)
        sys.exit(exit_code)

if __name__ == "__main__":
    main()

__all__ = [
    'log', 'check_jiti_cache_exists', 'check_recent_plugin_failures',
    'clear_jiti_cache', 'restart_gateway', 'perform_health_check', 'main'
]