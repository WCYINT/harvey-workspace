#!/bin/bash
echo "开始下载Chromium浏览器..."
echo "时间: $(date)"

# 创建日志文件
LOG_FILE="$HOME/chromium_download.log"
echo "=== Chromium下载日志 ===" > "$LOG_FILE"
echo "开始时间: $(date)" >> "$LOG_FILE"

# 尝试下载Chromium
echo "尝试使用npx agent-browser install..." | tee -a "$LOG_FILE"
cd /tmp

# 使用timeout避免无限等待
timeout 300 npx agent-browser install 2>&1 | tee -a "$LOG_FILE"

if [ $? -eq 0 ]; then
    echo "Chromium下载成功！" | tee -a "$LOG_FILE"
    echo "完成时间: $(date)" >> "$LOG_FILE"
    
    # 测试安装
    echo "测试安装..." | tee -a "$LOG_FILE"
    npx agent-browser --version 2>&1 | tee -a "$LOG_FILE"
else
    echo "Chromium下载超时或失败" | tee -a "$LOG_FILE"
    echo "将在下次运行时继续" >> "$LOG_FILE"
fi

echo "下载进程结束" | tee -a "$LOG_FILE"
echo "日志文件: $LOG_FILE"