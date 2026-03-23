# 回滚管理器技能

为 OpenClaw 提供版本升级、技能安装前的自动备份和故障快速回滚能力。

## 功能

- **自动备份**：在版本升级、技能安装前自动创建备份
- **手动备份**：随时创建带标签的备份
- **快速恢复**：系统故障时一键恢复到稳定版本
- **备份管理**：列出、清理旧备份

## 安装

```bash
# 1. 进入脚本目录
cd ~/.openclaw/workspace/scripts

# 2. 运行安装脚本
chmod +x install-rollback.sh
./install-rollback.sh

# 3. 确保 ~/bin 在 PATH 中
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

## 使用方法

### 基础命令

```bash
# 创建备份（建议在操作前执行）
oc-backup before-action

# 列出所有备份
oc-backup list

# 恢复到指定备份
oc-rollback 20250304_1200_before-action

# 清理30天前的旧备份
oc-backup cleanup 30
```

### 集成到工作流程

#### 方案一：手动备份（推荐）
在执行以下操作前**手动运行备份**：

1. **升级 OpenClaw**
   ```bash
   oc-backup before-upgrade
   npm install -g openclaw@latest
   ```

2. **安装新技能**
   ```bash
   oc-backup before-skill-install
   openclaw skill install <skill-name>
   ```

3. **更新技能**
   ```bash
   oc-backup before-skill-update
   openclaw skill update <skill-name>
   ```

#### 方案二：自动备份（通过包装脚本）
创建包装脚本 `safe-openclaw`：

```bash
#!/bin/bash
# 保存为 ~/bin/safe-openclaw
set -e

case "$1" in
    "skill"|"update"|"upgrade")
        ~/.openclaw/workspace/scripts/rollback-manager.sh auto-backup "$1"
        ;;
esac

# 执行原命令
openclaw "$@"
```

然后使用 `safe-openclaw` 代替 `openclaw`：

```bash
safe-openclaw skill install new-skill  # 会自动备份
```

## 备份内容

- `~/.openclaw/workspace/` - 工作空间（你的文件、配置、记忆）
- `~/.openclaw/*.{json,yaml,yml,md}` - 配置文件
- `~/.nvm/versions/node/v24.13.1/lib/node_modules/openclaw/` - OpenClaw 模块（可选恢复）

## 恢复流程

1. **识别问题**：系统无法启动、技能冲突、配置错误
2. **列出备份**：`oc-backup list`
3. **选择备份**：选择问题发生前的稳定版本
4. **执行恢复**：`oc-rollback <备份标签>`
5. **重启服务**：`openclaw gateway start`

## 最佳实践

1. **定期备份**：每周自动备份一次
   ```bash
   # 添加到 crontab
   0 2 * * 0 /Users/fhjtech/.openclaw/workspace/scripts/rollback-manager.sh backup weekly-auto
   ```

2. **操作前必备份**：
   - 升级前：`before-upgrade`
   - 安装技能前：`before-skill-install`
   - 修改配置前：`before-config-change`

3. **备份验证**：恢复后测试基本功能
   ```bash
   openclaw gateway status
   openclaw --version
   ```

4. **空间管理**：定期清理旧备份
   ```bash
   # 保留最近7天备份
   oc-backup cleanup 7
   ```

## 故障排除

### 恢复后服务无法启动
```bash
# 检查日志
openclaw gateway logs

# 尝试修复安装
npm install -g openclaw@latest
```

### 备份失败
- 检查磁盘空间：`df -h`
- 检查权限：`ls -la ~/.openclaw/`
- 查看日志：`cat ~/.openclaw/rollback.log`

### 命令找不到
```bash
# 确保 ~/bin 在 PATH 中
echo $PATH

# 手动运行脚本
~/.openclaw/workspace/scripts/rollback-manager.sh backup test
```

## 文件结构

```
~/.openclaw/backups/           # 备份存储目录
  20250304_1200_before-upgrade/
    workspace/                 # 工作空间副本
    *.json, *.yaml            # 配置文件
    module/                   # OpenClaw 模块（可选）
    backup.info              # 备份元数据
~/.openclaw/rollback.log      # 操作日志
~/bin/                       # 命令符号链接
  oc-backup -> rollback-manager.sh
  oc-rollback -> rollback-manager.sh
```

## 安全提示

- 备份包含敏感信息（API密钥、记忆等），请妥善保管
- 恢复操作会覆盖当前配置，请确认后再执行
- 建议将重要备份加密或存储在安全位置

## 更新日志

- v1.0 (2026-03-04): 初始版本，提供基础备份恢复功能