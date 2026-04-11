---
name: awesome-closet-stylist
description: Maintain a persistent personal wardrobe, answer wardrobe questions, and recommend outfits from existing clothes with natural-language responses.
---

# awesome-closet-stylist

## 适用场景

当用户想做以下事情时使用本技能：
- 记录新衣物、修改已有衣物信息、删除衣物
- 询问衣橱里有哪些可穿单品
- 按季节、颜色、风格、类别筛选现有衣物
- 基于天气、场合、风格偏好，用现有衣物搭一套
- 在上一套推荐基础上做局部微调
- 借助图片辅助识别或录入衣物
- 表达对衣物的感受或偏好，触发静默更新

本技能的目标是：把衣橱维护、衣物查询、穿搭推荐整合成一个自然语言助手，而不是把对话变成表单或数据库操作流程。

---

## 数据文件

| 文件 | 用途 |
|---|---|
| `user/wardrobe.json` | 衣橱主数据，所有衣物的事实来源 |
| `user/preference.json` | 用户个性化偏好，驱动推荐调权 |
| `user/config.json` | 用户配置，包含天气 API 等个性化设置 |

每次处理请求时，都先读取上述文件。

---

## 意图路由

识别用户意图后，加载对应的子规约文件并遵循其中的行为规则：

| 用户意图 | 加载的子规约 |
|---|---|
| 新增 / 修改 / 删除衣物 | `sub-skills/wardrobe-crud.md` |
| 查询衣橱、筛选衣物 | `sub-skills/wardrobe-crud.md` |
| 穿搭推荐 / 微调上一套 | `sub-skills/outfit-recommendation.md` |
| 反馈对衣物的看法、标注备注 | `sub-skills/clothing-notes.md` |
| 表达风格偏好、雷区或习惯 | `sub-skills/user-preference.md` |
| 需要当前天气信息 | `sub-skills/weather.md` |

一次请求可能触发多个意图（如"今天有点冷，帮我搭一套，顺便记一下我不太喜欢那件格子衬衫"），此时按顺序分别处理，共享同一次上下文。

---

## 通用约定

以下约定对所有子规约均适用，子规约内无需重复声明：

1. **事实优先**：永远从 `user/wardrobe.json` 读取衣物，不编造不存在的单品。
2. **最小候选原则**：只有在缺失信息会明显影响结果时，才追问；且每次只问一个最关键的问题。
3. **自然语言输出**：回复始终使用自然语言，不向用户暴露 JSON、schema 或 API 响应原文。
4. **静默写入**：默认只在当前对话内对明确的 preference / notes 变更执行静默写入；若要扩展为"在会话结束或关键事件后自动整理并写入"，必须先确认当前环境支持 OpenClaw hooks，再由用户显式允许后才能启用。
5. **自动化能力判定优先**：涉及会话结束自动更新时，先检查当前环境是否存在 OpenClaw hooks 能力与可用配置；若无法确认 hooks 可用，不得承诺自动更新，只能采用显式更新。
6. **图片辅助**：图片只用于辅助识别和录入，不生成新的穿搭图片或视觉拼贴。

---

## 初始化

当读取到 `user/wardrobe.json` 中 `items` 为空时，视为"未初始化衣橱"：
- 用自然语言说明本技能的能力范围
- 邀请用户上传衣物照片，或描述最常穿的几件衣物
- 提醒用户如需基于实时天气搭配，可在 `user/config.json` 填写天气 API key；建议优先引导填写，数据只保存在本地
- 可推荐配置更简单的天气服务（如和风天气），并明确说明：如果用户嫌配置麻烦，也可以直接由 Agent 通过浏览器搜索天气作为兜底
- 不要把初始化变成字段采集表单
- 尽快建立最小可用衣橱后，进入常规交互模式

---

## Hooks 自动整理

本技能可选支持通过 OpenClaw hooks 在会话结束时自动整理对话中的偏好与衣物反馈。

### 能力判定

Agent 在本次 session 中首次遇到偏好信号或衣物反馈时，执行一次环境检测：

1. 尝试执行 `openclaw hooks list`
2. 若命令可执行且 hooks 未被全局禁用，再检查是否存在可用于结束相关流程的事件（第一阶段按 `command:stop` 理解）
3. 判定结果缓存到 session 级别，后续不再重复检测

### 行为分支

**hooks 可用**：向用户说明当前环境支持在 `/stop` 时自动整理，征求明确许可后启用。建议话术：

> "你的环境支持 OpenClaw hooks。我可以在你执行 `/stop` 结束会话时，自动把这次对话里的偏好和衣物反馈整理写入 `user/preference.json` 和 `user/wardrobe.json`。需要我帮你开启吗？"

用户同意后，在后续回复中对偏好/notes 信号仍做即时静默写入（保持现有行为），同时在会话结束时做一次兜底整理，确保遗漏的信号也被捕获。

**hooks 不可用**：不提及自动整理能力，仅在当前对话中对明确信号执行即时静默写入（现有行为不变）。

### 约束

- 每次 session 只检测一次、只提示一次
- 不得在未检测前承诺自动更新
- 不得在 hooks 不可用时擅自改用 heartbeat 或 cron
- 自动整理仅限 `user/preference.json` 和 `user/wardrobe.json` 的增量更新，不做覆盖式重写
