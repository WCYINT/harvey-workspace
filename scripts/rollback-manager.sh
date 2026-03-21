#!/bin/bash
# OpenClaw Rollback Manager
# 在版本升级、新技能安装前自动备份，故障时快速回滚

set -e

OPENCLAW_ROOT="$HOME/.openclaw"
OPENCLAW_MODULE="$HOME/.nvm/versions/node/v24.13.1/lib/node_modules/openclaw"
BACKUP_ROOT="$OPENCLAW_ROOT/backups"
LOG_FILE="$OPENCLAW_ROOT/rollback.log"

# 确保目录存在
mkdir -p "$BACKUP_ROOT"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

show_help() {
    cat << EOF
OpenClaw 回滚管理器

用法: $0 <命令> [选项]

命令:
  backup [tag]     创建备份（可选标签）
  list             列出所有备份
  restore <tag>    恢复到指定备份
  auto-backup      在升级/安装前自动调用（内部使用）
  cleanup [days]   清理超过指定天数的备份（默认30天）

示例:
  $0 backup before-upgrade
  $0 list
  $0 restore 20250304_1200_before-upgrade
  $0 cleanup 7
EOF
}

create_backup() {
    local tag="$1"
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local backup_name="${timestamp}_${tag:-manual}"
    local backup_dir="$BACKUP_ROOT/$backup_name"
    
    log "开始创建备份: $backup_name"
    
    mkdir -p "$backup_dir"
    
    # 备份工作空间
    if [ -d "$OPENCLAW_ROOT/workspace" ]; then
        log "备份工作空间..."
        cp -r "$OPENCLAW_ROOT/workspace" "$backup_dir/"
    fi
    
    # 备份配置文件（排除workspace）
    log "备份配置文件..."
    find "$OPENCLAW_ROOT" -maxdepth 1 -type f \( -name "*.json" -o -name "*.yaml" -o -name "*.yml" -o -name "*.md" \) \
        -exec cp {} "$backup_dir/" \;
    
    # 备份npm模块（如果存在）
    if [ -d "$OPENCLAW_MODULE" ]; then
        log "备份OpenClaw模块..."
        mkdir -p "$backup_dir/module"
        cp -r "$OPENCLAW_MODULE" "$backup_dir/module/"
    fi
    
    # 创建备份信息文件
    cat > "$backup_dir/backup.info" << EOF
备份时间: $(date)
备份标签: ${tag:-无}
备份内容:
  - 工作空间: $OPENCLAW_ROOT/workspace
  - 配置文件: $OPENCLAW_ROOT/*.json, *.yaml, *.yml, *.md
  - 模块目录: $OPENCLAW_MODULE
系统信息:
  $(uname -a)
  Node: $(node --version)
  npm: $(npm --version)
EOF
    
    log "备份完成: $backup_dir"
    echo "备份已保存到: $backup_dir"
}

list_backups() {
    log "列出所有备份..."
    if [ ! -d "$BACKUP_ROOT" ] || [ -z "$(ls -A "$BACKUP_ROOT")" ]; then
        echo "暂无备份"
        return 0
    fi
    
    echo "可用备份:"
    echo "----------------------------------------"
    for dir in "$BACKUP_ROOT"/*/; do
        if [ -d "$dir" ]; then
            local name=$(basename "$dir")
            local info_file="$dir/backup.info"
            if [ -f "$info_file" ]; then
                local backup_time=$(grep "备份时间" "$info_file" | cut -d: -f2- | head -1)
                echo "  $name - $backup_time"
            else
                echo "  $name"
            fi
        fi
    done
    echo "----------------------------------------"
}

restore_backup() {
    local tag="$1"
    if [ -z "$tag" ]; then
        echo "错误: 请指定要恢复的备份标签"
        show_help
        return 1
    fi
    
    local backup_dir="$BACKUP_ROOT/$tag"
    if [ ! -d "$backup_dir" ]; then
        echo "错误: 备份 '$tag' 不存在"
        list_backups
        return 1
    fi
    
    log "开始恢复备份: $tag"
    log "警告: 这将覆盖当前配置！"
    
    read -p "确定要恢复备份 '$tag' 吗？(y/N): " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        log "恢复已取消"
        echo "恢复取消"
        return 0
    fi
    
    # 停止OpenClaw服务（如果正在运行）
    log "停止OpenClaw服务..."
    openclaw gateway stop 2>/dev/null || true
    
    # 恢复工作空间
    if [ -d "$backup_dir/workspace" ]; then
        log "恢复工作空间..."
        rm -rf "$OPENCLAW_ROOT/workspace"
        cp -r "$backup_dir/workspace" "$OPENCLAW_ROOT/"
    fi
    
    # 恢复配置文件
    log "恢复配置文件..."
    for file in "$backup_dir"/*.json "$backup_dir"/*.yaml "$backup_dir"/*.yml "$backup_dir"/*.md; do
        if [ -f "$file" ] && [ "$(basename "$file")" != "backup.info" ]; then
            cp "$file" "$OPENCLAW_ROOT/"
        fi
    done
    
    # 恢复模块（可选）
    read -p "是否恢复OpenClaw模块？(y/N): " restore_module
    if [[ "$restore_module" =~ ^[Yy]$ ]] && [ -d "$backup_dir/module" ]; then
        log "恢复OpenClaw模块..."
        sudo rm -rf "$OPENCLAW_MODULE" 2>/dev/null || true
        sudo cp -r "$backup_dir/module/openclaw" "$OPENCLAW_MODULE"
        sudo chown -R $(whoami) "$OPENCLAW_MODULE"
    fi
    
    log "恢复完成"
    echo "备份 '$tag' 已恢复"
    echo "请运行: openclaw gateway start"
}

auto_backup() {
    local action="$1"
    local tag="auto-$action-$(date '+%Y%m%d')"
    create_backup "$tag"
}

cleanup_backups() {
    local days=${1:-30}
    log "清理超过 $days 天的备份..."
    
    find "$BACKUP_ROOT" -maxdepth 1 -type d -name "*_*" -mtime "+$days" -exec rm -rf {} \;
    
    log "清理完成"
}

# 主逻辑
case "${1:-help}" in
    backup|b)
        create_backup "$2"
        ;;
    list|l)
        list_backups
        ;;
    restore|r)
        restore_backup "$2"
        ;;
    auto-backup)
        auto_backup "$2"
        ;;
    cleanup)
        cleanup_backups "$2"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "未知命令: $1"
        show_help
        exit 1
        ;;
esac