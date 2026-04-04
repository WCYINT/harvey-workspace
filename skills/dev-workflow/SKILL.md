---
name: dev-workflow
description: 完整开发工作流 - 一键执行从检查到封版的全流程
dependencies: version-manager, project-manager, dev-pipeline
license: Proprietary
---

# Dev Workflow - 完整开发工作流

整合 version-manager、project-manager 和 dev-pipeline，提供标准化的开发流程。

## 工作流程

```
                    dev-workflow
                         │
    ┌────────────────────┼────────────────────┐
    │                    │                    │
version-manager    project-manager      dev-pipeline
(版本管理)          (看板管理)           (代码生成)
    │                    │                    │
    └────────────────────┴────────────────────┘
                         │
                    标准化流程
```

## 命令

### dev-start <project> [version]

启动新的开发迭代：

```bash
# 自动检测最新版本
$ dev-start gemini-agent
Found latest version: v1.3.4
Preparing workspace...
✅ Ready to develop v1.3.5

# 指定基础版本
$ dev-start gemini-agent v1.3.4
Preparing v1.3.4...
✅ Ready to develop v1.3.5
```

执行步骤：
1. `version-check gemini-agent` - 检查当前状态
2. `version-prepare gemini-agent v1.3.4` - 准备代码
3. `version-validate gemini-agent` - 验证完整性
4. `project-update gemini-agent --status "开发中"` - 更新看板

### dev-status <project>

查看项目开发状态：

```bash
$ dev-status gemini-agent

项目: Gemini Agent Client
============================

版本状态:
  最新封版: v1.3.4
  当前开发: v1.3.5
  工作目录: ✅ 已准备 (基于 v1.3.4)

文件校验:
  css/components.css: ✅ 20325 bytes (matches online)
  js/app.js: ✅ 8234 bytes (matches online)
  js/ui.js: ✅ 5425 bytes (matches online)

看板状态:
  状态: 🟢 开发中
  最后改动: 2026-02-23 06:45:00
  备注: 开始v1.3.5开发

下一步:
  1. 编写需求文档
  2. 执行: dev-pipeline analyze
```

### dev-analyze <project>

执行架构分析（包装dev-pipeline）：

```bash
$ dev-analyze gemini-agent
Reading requirements from versions/v1.3.5/docs/REQUIREMENTS.md...
Running dev-pipeline analyze...

✅ 分析完成，等待确认...
```

### dev-write <project>

执行代码编写（确认后）：

```bash
$ dev-write gemini-agent
确认analyze结果后继续...
Running dev-pipeline write...

✅ 代码生成完成
```

### dev-review <project>

执行代码审查：

```bash
$ dev-review gemini-agent
Running dev-pipeline review...

✅ 审查通过 / ⚠️ 发现问题，执行 dev-fix
```

### dev-fix <project>

修复代码问题：

```bash
$ dev-fix gemini-agent
Running dev-pipeline fix...

✅ 修复完成，请重新审查: dev-review
```

### dev-deploy <project>

部署到生产环境：

```bash
$ dev-deploy gemini-agent
Pre-deployment checks:
  ✅ Backup created: backup-1234567890.tar.gz
  ✅ File size validated (diff < 20%)
  ✅ Critical functions present

Deploy to production? [y/N]: y
Running dev-pipeline deploy...

✅ Deployed to 14.103.210.113:3002
```

执行步骤：
1. `version-validate gemini-agent` - 最终验证
2. 备份线上代码
3. 红线检查（文件大小、关键函数）
4. `dev-pipeline deploy` - 执行部署

### dev-seal <project> <version>

封版并归档：

```bash
$ dev-seal gemini-agent v1.3.5
Sealing version v1.3.5...

执行步骤:
  ✅ version-archive gemini-agent v1.3.5
  ✅ project-update gemini-agent --version v1.3.5 --status "已封版"
  ✅ project-changelog gemini-agent release --version v1.3.5
  ✅ dev-pipeline seal

📋 封版完成:
  版本: v1.3.5
  位置: versions/v1.3.5/
  看板: 已更新
  日志: 已记录
```

## 完整开发流程示例

### 场景：开发新功能

```bash
# 1. 启动开发
$ dev-start gemini-agent
Found latest version: v1.3.4
Preparing workspace...
✅ Ready to develop v1.3.5

# 2. 编写需求（手动编辑REQUIREMENTS.md后）
# 使用你喜欢的编辑器编辑 versions/v1.3.5/docs/REQUIREMENTS.md

# 3. 架构分析
$ dev-analyze gemini-agent
✅ 分析完成，等待确认

# [用户确认后]

# 4. 编写代码
$ dev-write gemini-agent
✅ 代码生成完成

# 5. 代码审查
$ dev-review gemini-agent
✅ 审查通过

# 6. 部署
$ dev-deploy gemini-agent
✅ 部署完成

# 7. 封版
$ dev-seal gemini-agent v1.3.5
✅ 封版完成
```

## 状态检查点

### 检查点1：启动时
```
dev-start 自动执行:
  ✓ version-check
  ✓ version-prepare
  ✓ version-validate
  ✓ project-update (status="开发中")
```

### 检查点2：部署前
```
dev-deploy 自动执行:
  ✓ 备份线上
  ✓ version-validate
  ✓ 红线检查 (文件大小差异<20%)
  ✓ 用户确认
```

### 检查点3：封版时
```
dev-seal 自动执行:
  ✓ version-archive
  ✓ project-update (version, status)
  ✓ project-changelog
  ✓ dev-pipeline seal
```

## 错误恢复

### 部署失败
```bash
$ dev-deploy gemini-agent
❌ Deployment failed

Recovery options:
  1. Rollback: dev-rollback gemini-agent
  2. Fix and retry: dev-fix gemini-agent && dev-deploy gemini-agent
  3. Check status: dev-status gemini-agent
```

### 验证失败
```bash
$ dev-start gemini-agent
❌ Validation failed
  css/components.css: size mismatch
    Local:  16137 bytes
    Remote: 20325 bytes (-21%)

Possible causes:
  - Working directory not prepared correctly
  - Online version is newer than local archive

Actions:
  1. Check online: version-check gemini-agent
  2. Sync from online: version-sync gemini-agent
  3. Force prepare: version-prepare gemini-agent v1.3.4 --force
```

## 配置

`.dev-workflow/config.json`:

```json
{
  "projects": {
    "gemini-agent": {
      "auto_backup": true,
      "size_threshold": 20,
      "require_confirm": {
        "analyze": true,
        "deploy": true,
        "seal": false
      }
    }
  }
}
```

## 与现有skill的关系

| 命令 | 调用的skill | 说明 |
|------|------------|------|
| dev-start | version-manager, project-manager | 启动流程 |
| dev-status | version-manager, project-manager | 状态查询 |
| dev-analyze | dev-pipeline | 架构分析 |
| dev-write | dev-pipeline | 代码生成 |
| dev-review | dev-pipeline | 代码审查 |
| dev-fix | dev-pipeline | 代码修复 |
| dev-deploy | version-manager, dev-pipeline | 部署流程 |
| dev-seal | version-manager, project-manager, dev-pipeline | 封版流程 |

## 安全规则

1. **禁止绕过validate** - 每次deploy前必须验证
2. **禁止无备份deploy** - 必须创建备份才能部署
3. **禁止无确认analyze** - analyze后必须用户确认
4. **禁止手动改代码** - 必须通过dev-pipeline write
5. **禁止无seal归档** - 封版必须通过dev-seal
