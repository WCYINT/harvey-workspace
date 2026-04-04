# Work Style Memory

将重复性多步骤任务转化为可复用的本地 Workflow / SOP，支持 Codex、OpenClaw 或同类 Agent 运行时。

---

## 简介

`work-style-memory` 是一个将"你的做事方式"沉淀成本地 Workflow / SOP 的 skill。

它适合这样的场景：

- 你经常让 agent 处理同类多步骤任务
- 你希望 agent 先检查有没有现成 SOP，而不是每次从头开始
- 你希望 agent 在执行前先问一句"发现已有流程，是否复用？"
- 你希望任务做完后，可以把这次过程保存成新的 workflow，或者更新旧 workflow

这个项目把 workflow 存成可编辑的本地 JSON 文件，并提供：

- **Runtime 侧**：匹配、复用确认、brief 生成、保存与更新
- **本地 UI 侧**：浏览、编辑、删除、JSON 预览

## 核心理念

- Workflow 是结构化的记忆，而非巨大的提示词
- 匹配到的 SOP 应该先询问，而不是静默执行
- UI 只负责编辑 workflow 文件，不模拟运行时对话行为
- Workflow 文件是唯一真相来源

## 功能特性

- 重复任务的 workflow 匹配
- 复用匹配 SOP 前的明确确认
- 将 workflow 渲染为执行摘要（Execution Brief）
- 真实任务完成后的草稿捕获与保存/更新
- 本地 UI：浏览、编辑、删除、预览 workflows
- 支持 Unicode 友好的 workflow 名称和文件路径

## 运行流程

推荐的四阶段流程：

1. **匹配（Match）**：在重复任务执行前，检查已保存的 workflow 库
2. **询问（Ask）**：若有高置信度匹配，询问用户是否复用
3. **执行（Execute）**：用户同意后，将 workflow 编译为执行摘要并执行任务
4. **保存（Capture）**：任务完成后，询问是否保存新 workflow 或更新已有 workflow

**重要原则**：除非用户在本轮明确要求复用已有流程，否则不得静默执行匹配到的 SOP。

## Workflow 格式

每个 workflow 存储为一个 JSON 文件。

```json
{
  "id": "pr-review",
  "name": "PR Review",
  "summary": "以风险优先的方式审查 Pull Request",
  "match": {
    "keywords": ["pr", "review", "diff"]
  },
  "steps": [
    {
      "id": "step-1",
      "title": "步骤 1",
      "instruction": "获取 PR 信息",
      "tool": "github"
    }
  ],
  "tool_preferences": [
    {
      "tool": "github",
      "purpose": "加载 PR 元数据和评论"
    }
  ],
  "version": 1
}
```

## 快速开始

### 创建 workflow

```bash
python3 scripts/new_workflow.py "PR Review" --dir /tmp/workflows
```

### 匹配任务

```bash
python3 scripts/match_workflows.py \
  "帮我 review 这个 PR，排查潜在回归" \
  --dir /tmp/workflows \
  --tools git,github
```

### 渲染执行摘要

```bash
python3 scripts/render_workflow_prompt.py \
  /tmp/workflows/pr-review.json \
  --task "帮我 review 这个 PR"
```

### 从真实任务保存 workflow

```bash
python3 scripts/save_workflow.py \
  "帮我 review PR" \
  --dir /tmp/workflows \
  --steps $'获取 PR 信息\n检查风险变化\n写出发现' \
  --tools git,github
```

## 本地 UI

启动编辑器：

```bash
python3 ui/server.py --dir ./.openclaw/workflows
```

然后打开浏览器访问：

```
http://127.0.0.1:8765
```

UI 的作用范围仅限于 workflow 管理：

- 浏览 workflow 列表
- 编辑 workflow 字段
- 删除 workflow
- 预览 JSON

运行时匹配和复用询问属于 Agent 对话流程的一部分，不在编辑器内进行。

## 安装

将文件夹复制到本地 skills 目录，然后重启或开启新会话即可。

```bash
cp -R work-style-memory /path/to/skills/
```

Workflow 存储路径推荐：

- 项目级：`./.openclaw/workflows`
- 个人全局：`$CODEX_HOME/work-style-memory/workflows`

## 项目结构

```
work-style-memory/
├── SKILL.md                        # Skill 主说明
├── instruction.md                  # 使用说明
├── README.md                       # 本文件
├── assets/                         # 资源文件
│   └── workflow-template.json      # Workflow JSON 模板
├── references/                     # 技术参考文档
│   ├── workflow-schema.md          # Workflow JSON Schema 规范
│   ├── runtime-behavior.md         # 运行时行为规范
│   └── local-ui-spec.md            # 本地 UI 产品规格说明
├── scripts/                        # 核心脚本
│   ├── workflow_engine.py          # 核心引擎（匹配/评分/渲染）
│   ├── match_workflows.py          # CLI：匹配 workflow
│   ├── capture_workflow.py         # CLI：从任务生成草稿
│   ├── new_workflow.py             # CLI：新建空白 workflow
│   ├── save_workflow.py            # CLI：保存或更新 workflow
│   └── render_workflow_prompt.py   # CLI：渲染执行摘要
└── ui/                             # 本地编辑器 UI
    ├── server.py                   # HTTP 服务器
    └── static/                     # 前端文件（HTML/CSS/JS）
```

## 相关文档

- [instruction.md](./instruction.md)
- [references/workflow-schema.md](./references/workflow-schema.md)
- [references/runtime-behavior.md](./references/runtime-behavior.md)
- [references/local-ui-spec.md](./references/local-ui-spec.md)

## License

[MIT](./LICENSE)
