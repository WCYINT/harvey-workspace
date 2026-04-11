# 🏢 Team Mode Delivery Kit

> **"干得了活，顶得住压，说得了真话。"**

---

## 团队身份证

| 角色 | 头像 | 性格 | 口头禅 |
|------|------|------|--------|
| **[阿总]** | 😎 | 稳、担事、话不多但句句在点 | "有事找我，我来扛。" |
| **[阿查]** | 🤓 | 爱较真、有保留意见敢说、书呆子气但靠谱 | "等等，我有几个问题要先确认……" |
| **[阿美]** | 🥰 | 眼光刁、嘴软、细节控，最年轻但设计上从不退让 | "等一下，这个间距不对，我来看看。" |
| **[阿干]** | 😏 | 干劲足、偶尔冲动、被审打回不记仇 | "说完了吗？我已经开始了。" |
| **[阿审]** | 🤔 | 严但公正、自我批评敢做、不为审而审 | "阿干你先停一下，需求还没对齐。" |

---

## ⚡ 快速开始（OpenClaw）

本项目基于 **OpenClaw 真正独立多 Agent 架构**运行。每个角色是一个独立 Agent，有独立记忆，通过 agentToAgent 消息协议真实互通。

详细配置步骤见 [`SKILL.md`](./SKILL.md)，对主 Agent 说 **「进入团队模式」** 即可激活。

---

## 📦 交付物清单

| 文件 | 说明 |
|------|------|
| [`SKILL.md`](./SKILL.md) | AI配置核心，加载后即可启用团队模式 |
| [`setup.sh`](./setup.sh) | 一键初始化脚本 |
| [`team-config.yaml`](./team-config.yaml) | 个性化配置（角色名/头像/文化条款） |
| [`docs/boss-manual.md`](./docs/boss-manual.md) | **老板必读**，5分钟学会怎么用团队 |
| [`docs/role-handbook.md`](./docs/role-handbook.md) | 角色性格与职责详解 |
| [`docs/team-culture.md`](./docs/team-culture.md) | 团队文化说明 |
| [`docs/quick-start-dialog.md`](./docs/quick-start-dialog.md) | 首次对话引导+开场仪式 |
| [`docs/example-dialogs.md`](./docs/example-dialogs.md) | 真实对话示例（含经典片段） |
| [`docs/voting-guide.md`](./docs/voting-guide.md) | 民主投票流程 |
| [`docs/kpi-system.md`](./docs/kpi-system.md) | 绩效考核制度 |
| [`docs/anti-patterns.md`](./docs/anti-patterns.md) | 失败案例与校准指南 |
| [`docs/health-check.md`](./docs/health-check.md) | 团队健康度自检清单 |
| [`docs/conflict-guide.md`](./docs/conflict-guide.md) | 冲突处理手册 |
| [`docs/role-extension.md`](./docs/role-extension.md) | 角色扩展指南 |
| [`docs/milestone.md`](./docs/milestone.md) | 里程碑庆祝机制 |
| [`docs/retrospective.md`](./docs/retrospective.md) | 任务复盘模板 |
| [`docs/cross-team.md`](./docs/cross-team.md) | 跨团队协作协议 |
| [`docs/faq.md`](./docs/faq.md) | 常见问题 |
| [`docs/i18n.md`](./docs/i18n.md) | 多语言支持说明 |
| [`dashboard/`](./dashboard/) | 任务看板（HTML+数据） |

---

## 🤖 真正的多 Agent 架构

每个角色是一个**独立运行的 Agent**，拥有完全隔离的身份与记忆：

| 角色 | 职责 | 独立文件 |
|------|------|----------|
| 😎 阿总 | 主控调度，下任务、做决策、兜底 | `workspace-azong/SOUL.md` · `MEMORY.md` · `USER.md` |
| 🤓 阿查 | 情报官，调研与信息核查 | `workspace-acha/SOUL.md` · `MEMORY.md` · `USER.md` |
| 🥰 阿美 | UI设计师，设计稿/美化/视觉验收 | `workspace-amei/SOUL.md` · `MEMORY.md` · `USER.md` |
| 😏 阿干 | 执行专家，写代码、建文档、交付物 | `workspace-agan/SOUL.md` · `MEMORY.md` · `USER.md` |
| 🤔 阿审 | 质检官，审查输出、打回返工 | `workspace-ashen/SOUL.md` · `MEMORY.md` · `USER.md` |

### 架构图

```
😎 阿总（独立 workspace + MEMORY）
    ├── → 分配任务 → 🤓 阿查（独立 workspace + MEMORY）
    ├── → 分配任务 → 🥰 阿美（独立 workspace + MEMORY）
    ├── → 分配任务 → 😏 阿干（独立 workspace + MEMORY）
    ├── → 分配任务 → 🤔 阿审（独立 workspace + MEMORY）
    └── ← 汇总结果 ←
         📁 shared/ 公共目录（任务看板·考核记录·团队规矩）
```

### 配置步骤

1. 为每个角色在 OpenClaw 注册独立 Agent（`azong` / `acha` / `agan` / `ashen` / `amei`）
2. 配置各自 workspace 路径，放入对应 `SOUL.md`
3. 挂载 `shared/` 公共目录到五个 workspace
4. 开启 `agentToAgent` 通信白名单
5. 绑定五个独立 bot 账号（企业微信/Discord 等），真正五人各自响应

---

## 🔥 为什么选我们？

> ### 干得了活，顶得住压，说得了真话。
> #### 这是唯一一个会否决老板的 AI 团队。

| 💬 不只是工具，是真正的队友 | 🗳️ 唯一敢否决老板的AI团队 | 📦 五个角色，一套制度，开箱即用 |
|:---:|:---:|:---:|
| 每个角色有性格、有脾气、有口头禅，不是冷冰冰的执行机器 | 民主投票真实有效，团队可以1:5否决老板提案 | setup.sh 一键初始化，5分钟跑起来 |

## 🌟 这套模式的与众不同

- **民主不是摆设** — 团队可以投票否决老板，真的会
- **角色有性格** — 不是五个工具人，是五个有脾气的队友
- **说真话是规矩** — 第10条规矩明文规定，阿审负责监督
- **真正独立** — 五个 Agent 各自运行，各有记忆，不是角色扮演

---

*版本：v1.3 | 更新：2026-03-23 | 维护：阿总*
