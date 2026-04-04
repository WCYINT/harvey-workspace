#!/usr/bin/env python3
"""
OpenClaw Gateway Watchdog
检查 Gateway 是否宕机超过5小时，如果是则自动重启
"""
import re
import subprocess
import os
import stat
from datetime import datetime, timedelta
from typing import Optional

GATEWAY_LABEL = "ai.openclaw.gateway"
GATEWAY_PORT = 18789
DOWN_THRESHOLD_HOURS = 5
LOG_FILE = "/Users/fhjtech/.openclaw/logs/gateway_watchdog.log"
GATEWAY_ERR_LOG = "/Users/fhjtech/.openclaw/logs/gateway.err.log"

def log(msg: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def is_gateway_running() -> tuple[bool, Optional[subprocess.CompletedProcess]]:
    """检查 Gateway 进程是否在运行; 返回 (is_running, launchctl_result)"""
    try:
        result = subprocess.run(
            ["launchctl", "list", GATEWAY_LABEL],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            return False, result
        # Parse "PID" = 12345; must be positive integer to confirm running
        m = re.search(r'"PID"\s*=\s*(\d+)', result.stdout)
        if not m:
            return False, result
        return int(m.group(1)) > 0, result
    except Exception:
        return False, None

def get_last_error_time() -> Optional[datetime]:
    """获取 gateway.err.log 最后修改时间"""
    try:
        mtime = os.path.getmtime(GATEWAY_ERR_LOG)
        return datetime.fromtimestamp(mtime)
    except Exception:
        return None

def _bootout() -> subprocess.CompletedProcess:
    """向当前 GUI domain 发送 bootout（忽略 112 退出码）"""
    result = subprocess.run(
        ["launchctl", "bootout", f"gui/{os.getuid()}/{GATEWAY_LABEL}"],
        capture_output=True, text=True
    )
    return result

def _bootstrap() -> subprocess.CompletedProcess:
    """从 LaunchAgents plist 执行 bootstrap"""
    return subprocess.run(
        ["launchctl", "bootstrap", f"gui/{os.getuid()}",
         "/Users/fhjtech/Library/LaunchAgents/ai.openclaw.gateway.plist"],
        capture_output=True, text=True
    )

def _restart_gateway(reason: str) -> None:
    """统一的重启流程：bootout -> bootstrap"""
    log(f"[{reason}] 执行重启...")
    bootout_result = _bootout()
    if bootout_result.returncode != 0:
        stderr = bootout_result.stderr.strip()
        # 退出码 112 = 无此进程（label 存在但 job 已死），不算致命错误
        if "112" not in stderr and "No such file" not in stderr:
            log(f"bootout 失败: {stderr}")
    bootstrap_result = _bootstrap()
    if bootstrap_result.returncode == 0:
        log("Gateway 重启完成")
    else:
        log(f"bootstrap 失败: {bootstrap_result.stderr.strip()}")

def main() -> None:
    log("Watchdog 检查开始")
    
    # 检查 Gateway 是否在运行
    is_running, lc_result = is_gateway_running()
    if is_running:
        log("Gateway 运行正常，无需干预")
        return
    
    log("Gateway 未运行，开始检查宕机时长...")
    
    # 检查宕机时长
    last_err_time = get_last_error_time()
    if last_err_time is None:
        # gateway.err.log 不存在或无法访问，无法通过文件时间判断宕机时长。
        # 通过 launchctl list 结果判断 label 状态，避免重复调用。
        log(f"无法获取 {GATEWAY_ERR_LOG} 的修改时间（文件不存在或无权限）")
        if lc_result is None:
            # launchctl 自身异常，保守处理，仅记录
            log("launchctl 调用异常，跳过自动干预")
            return
        if lc_result.returncode != 0 or "Could not find" in lc_result.stderr:
            # label 从未注册过，执行首次引导
            log("Gateway label 未注册，执行首次引导...")
            bootstrap_result = _bootstrap()
            if bootstrap_result.returncode == 0:
                log("Gateway 首次引导已完成")
            else:
                log(f"bootstrap 失败: {bootstrap_result.stderr.strip()}")
        else:
            # label 存在但进程死了，尝试 bootout 再 bootstrap
            log("Gateway label 存在但进程异常，执行重启...")
            _restart_gateway("进程异常")
        return
    
    downtime = datetime.now() - last_err_time
    downtime_hours = downtime.total_seconds() / 3600
    log(f"Gateway 宕机时长: {downtime_hours:.1f} 小时（阈值: {DOWN_THRESHOLD_HOURS} 小时）")
    
    if downtime_hours >= DOWN_THRESHOLD_HOURS:
        log(f"宕机超过 {DOWN_THRESHOLD_HOURS} 小时，自动重启 Gateway...")
        _restart_gateway(f"宕机 {downtime_hours:.1f}h")
    else:
        log(f"宕机未超过阈值（{downtime_hours:.1f}h < {DOWN_THRESHOLD_HOURS}h），不干预")

if __name__ == "__main__":
    main()

__all__ = ['log', 'is_gateway_running', 'get_last_error_time', 'main']
