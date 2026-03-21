#!/bin/bash
# 安装回滚管理器

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROLLBACK_SCRIPT="$SCRIPT_DIR/rollback-manager.sh"
TARGET_BIN="$HOME/bin"

# 确保脚本可执行
chmod +x "$ROLLBACK_SCRIPT"

# 创建 bin 目录（如果不存在）
mkdir -p "$TARGET_BIN"

# 创建符号链接
ln -sf "$ROLLBACK_SCRIPT" "$TARGET_BIN/oc-backup"
ln -sf "$ROLLBACK_SCRIPT" "$TARGET_BIN/oc-rollback"

# 创建别名建议
cat << EOF
✅ 回滚管理器安装完成！

可用命令:
  oc-backup [tag]      创建备份
  oc-backup list       列出备份
  oc-rollback <tag>    恢复备份

使用方法:
1. 在升级或安装新技能前:
   oc-backup before-upgrade

2. 查看可用备份:
   oc-backup list

3. 恢复备份:
   oc-rollback 20250304_1200_before-upgrade

4. 自动备份（在脚本中调用）:
   $ROLLBACK_SCRIPT auto-backup upgrade

建议将 ~/bin 添加到 PATH 环境变量:
  echo 'export PATH="$HOME/bin:\$PATH"' >> ~/.zshrc
  source ~/.zshrc

备份目录: ~/.openclaw/backups/
日志文件: ~/.openclaw/rollback.log
EOF

# 检查 PATH
if [[ ":$PATH:" != *":$TARGET_BIN:"* ]]; then
    echo ""
    echo "⚠️  注意: ~/bin 不在 PATH 中，请按上述建议添加"
fi