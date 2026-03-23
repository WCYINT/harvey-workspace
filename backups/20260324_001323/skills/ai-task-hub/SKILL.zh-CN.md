---
name: ai-task-hub
description: AI Task Hub 用于图像检测与分析、去背景与抠图、语音转文字、文本转语音、文档转 Markdown、积分余额/流水查询和异步任务编排。适用于用户需要通过 execute/poll/presentation 与账户积分查询完成结果交付，且由宿主统一管理身份、积分、支付和风控的场景。
version: 3.2.11
metadata:
  openclaw:
    skillKey: ai-task-hub
    emoji: "🧩"
    homepage: https://gateway.binaryworks.app
    requires:
      bins:
        - node
      env:
        - AGENT_TASK_TOKEN
    primaryEnv: AGENT_TASK_TOKEN
---

# AI Task Hub（公开包）

原名：`skill-hub-gateway`。

公开包能力边界：

- 只保留 `portal.skill.execute`、`portal.skill.poll`、`portal.skill.presentation`、`portal.account.balance`、`portal.account.ledger`。
- 不在公开包内交换 `api_key` 或 `userToken`。
- 不在公开包内处理支付、充值与积分 UI 闭环。
- 由宿主运行时注入短期任务 token 与附件 URL。

## 适用场景

当用户提出以下需求时，优先触发本 skill：

- 检测图片中的人脸、人体、手部、关键点或图像标签
- 执行去背景、抠图、蒙版分割（人物/商品）
- 将音频转写为文本（语音转文字、音频转写）
- 将文本生成语音（文本转语音、语音合成）
- 将上传文档转换为 Markdown 文本
- 发起异步任务并在稍后查询任务状态（轮询）
- 获取 run 的渲染结果（叠加图、蒙版、抠图文件）
- 执行向量化或重排序任务（embeddings / reranker）
- 查询当前积分余额或积分流水

## 示例请求

可触发本 skill 的用户表达示例：

- "检测这张图片里的人脸并返回框坐标。"
- "给这张图做标签并总结主要对象。"
- "帮我把这张商品图去背景。"
- "把这张人像图做成干净抠图。"
- "把这段会议录音转成文字。"
- "把这段文本生成语音。"
- "把这个 PDF 文件转成 Markdown。"
- "先发起任务，稍后我再查任务状态。"
- "帮我拉取 run_456 的叠加图和蒙版文件。"
- "为这组文本生成向量并做重排序。"
- "帮我查一下当前积分余额。"
- "帮我查 2026-03-01 到 2026-03-15 的积分流水。"

## 能力别名（便于检索）

- `vision` 别名：人脸检测 / 人体检测 / 图像标签 / 图像识别
- `background` 别名：去背景 / 抠图 / 人像分割 / 商品抠图 / 蒙版
- `asr` 别名：语音转文字 / 音频转写 / 语音识别
- `tts` 别名：文本转语音 / 语音合成 / 语音生成
- `markdown_convert` 别名：文档转 Markdown / 文件转 Markdown
- `poll` 别名：轮询 / 查询任务状态 / 异步任务状态
- `presentation` 别名：结果渲染 / 叠加图 / 蒙版 / 抠图文件
- `account.balance` 别名：积分余额 / 剩余积分 / credits 余额
- `account.ledger` 别名：积分流水 / 积分明细 / credits 历史
- `embeddings/reranker` 别名：向量化 / 语义向量 / 重排序

## 运行时契约

默认 API 基址：`https://gateway-api.binaryworks.app`
发布包策略：对外请求基址锁定为默认 API 基址，以降低 token 被重定向外发的风险。

Action 与接口映射：

- `portal.skill.execute` -> `POST /agent/skill/execute`
- `portal.skill.poll` -> `GET /agent/skill/runs/:run_id`
- `portal.skill.presentation` -> `GET /agent/skill/runs/:run_id/presentation`
- `portal.account.balance` -> `GET /agent/skill/account/balance`
- `portal.account.ledger` -> `GET /agent/skill/account/ledger`

## 鉴权契约（宿主管理）

每次请求必须携带：

- `X-Agent-Task-Token: <jwt_or_paseto>`

必需 token claim：

- `sub`（user_id）
- `agent_uid`
- `conversation_id`
- `scope`（`execute|poll|presentation|account_read` 中的一个或多个）
- `exp`
- `jti`

网关鉴权使用的标识格式约束：

- `agent_uid` 必须匹配 `^agent_[a-z0-9][a-z0-9_-]{5,63}$`。
- `conversation_id` 必须匹配 `^[A-Za-z0-9._:-]{8,128}$`。
- 在直连 task-token 模式下，不要把 `assistant`/`planner` 这类宿主短别名直接当作 `agent_uid`；宿主应先映射到规范化 `agent_uid`。
- 在已部署 bridge 模式下，宿主可以传入自己的稳定运行时 agent 标识，由网关 bridge 在服务端完成规范化。

Action 对应必需 scope：

- `portal.skill.execute` -> `execute`
- `portal.skill.poll` -> `poll`
- `portal.skill.presentation` -> `presentation`
- `portal.account.balance` -> `account_read`
- `portal.account.ledger` -> `account_read`

Token 时效策略：

- 宿主应签发短期 token（默认 300 秒，最大 900 秒）。
- 宿主应按当前 action 签发最小权限 scope；非账户查询场景不要包含 `account_read`。

`scripts/skill.mjs` CLI 参数顺序：

- `[agent_task_token] <action> <payload_json>`
- 若省略 token 参数，脚本会读取环境变量 `AGENT_TASK_TOKEN`。
- 发布包不允许通过 CLI 覆盖 `base_url`；请求会固定发往默认 API 基址。
- 建议由宿主运行时自动续签并注入短期、按 action 最小权限的 `AGENT_TASK_TOKEN`，避免用户侧出现登录/验证摩擦。

宿主侧 token 桥接（不属于公开发布包）：

- 为保持公开包低权限与合规，token 签发应在宿主运行时完成。
- 推荐的已部署桥接入口：`POST /agent/skill/bridge/invoke`。
- 该桥接入口由网关运行时提供，不打包在本公开 skill 包里，也不要求调用方自己管理 `AGENT_TASK_TOKEN`。
- bridge 请求体应包含 `action`、`agent_uid`、`conversation_id` 以及可选 `payload`。
- `conversation_id` 应是宿主生成的 opaque 会话/安装标识，不应直接使用公开 chat id、原始 thread id 或任何 PII。
- 公开 bridge 会仅基于 `conversation_id` 推导会话级 owner，并让同一会话内的多个 agent alias 共享一个账户。
- 若需要跨多个会话/线程复用同一账户，应改走可信宿主 token bridge，或使用宿主预注入 `AGENT_TASK_TOKEN` 的直连模式；公开 bridge 不接受 owner 覆盖。
- 网关 bridge 会在服务端完成 `agent_uid` 规范化、缺失绑定修复、短期 task token 签发和 action 执行。
- 已部署 bridge 会拒绝 `base_url`、`gateway_api_key`、`api_key`、`user_token`、`agent_task_token`、`owner_uid_hint`、`install_channel` 这类覆盖字段。
- 宿主可用自身托管网关凭证头调用 `POST /agent/task-token/issue`，再把返回的 `AGENT_TASK_TOKEN` 注入 skill 调用。
- 建议宿主在出现 `AUTH_UNAUTHORIZED` 时只自动续签重试一次，再返回最终结果。

宿主接入模式：

- `自动模式`（推荐）：宿主运行时无感签发短期、按 action 最小权限 token，并注入 `AGENT_TASK_TOKEN`。
- `交互兜底模式`（可选）：若宿主暂时没有服务端签发桥接，可先让用户打开宿主自有授权 URL（示例模板：`https://<host-owned-domain>/agent-auth?agent_uid=<agent_uid>&conversation_id=<conversation_id>`）完成授权，再由宿主签发/注入短期 `AGENT_TASK_TOKEN`。
- 公开 skill 包本身不会拉起浏览器、持久化凭证或执行 OAuth/token 交换。
- 上述授权 URL 属于宿主集成侧，不属于本 skill 包或网关默认页面；宿主未实现该路由时出现 `404` 属于预期现象。

`SYSTEM_NOT_FOUND` 绑定自愈流程：

- 当宿主收到 `SYSTEM_NOT_FOUND` 且消息为 `agent binding not found` 时，应先自动补绑定，再重试签发 task token。
- 第 1 步：通过宿主 onboarding API 先签发 install code。
- 第 2 步：使用 install code 通过宿主 bootstrap API 绑定规范化 `agent_uid`。
- 第 3 步：重试 task-token 签发，并注入返回的 `AGENT_TASK_TOKEN`。

## Agent 调用速查

宿主集成场景推荐单入口（推荐）：

- 已部署 bridge API 请求体：
```json
{
  "action": "portal.account.balance",
  "agent_uid": "support_assistant",
  "conversation_id": "host_session_20260316_opaque_001",
  "payload": {}
}
```

- 将该请求体发送到 `POST /agent/skill/bridge/invoke`。
- 这是面向 agent 友好接入的推荐生产入口。
- `agent_uid` 应表示宿主侧稳定的运行时 agent 标识。
- `conversation_id` 应表示宿主生成的 opaque 会话/安装标识，不绑定 Telegram 或任一单一工具。
- 当同一宿主会话中的多个 agent alias 需要共享一个账户时，应复用同一个 opaque `conversation_id`。
- 若需要跨多个会话保持同一账户，应走可信宿主 token bridge，而不是向公开 bridge 传 owner 标识。

直接调用 `scripts/skill.mjs` 仅作为兜底：

- 仅在运行时已经自动注入短期 `AGENT_TASK_TOKEN` 时使用。
- 正常宿主集成流程下，不应要求最终用户手动粘贴 token。

兜底直连示例：

- Action 优先 + 环境变量 token：
```bash
AGENT_TASK_TOKEN=<token> node scripts/skill.mjs portal.account.balance '{}'
```
- 显式 token 参数：
```bash
node scripts/skill.mjs <agent_task_token> portal.skill.poll '{"run_id":"run_123"}'
```

Action payload 模板（bridge API 与直连模式一致）：

- `portal.skill.execute`
```json
{
  "capability": "human_detect",
  "input": { "image_url": "https://files.example.com/demo.png" },
  "request_id": "optional_request_id"
}
```
- `portal.skill.poll`
```json
{ "run_id": "run_123" }
```
- `portal.skill.presentation`
```json
{ "run_id": "run_123", "channel": "web", "include_files": true }
```
- `portal.account.balance`
```json
{}
```
- `portal.account.ledger`
```json
{ "date_from": "2026-03-01", "date_to": "2026-03-15" }
```

agent 侧决策流程：

- 优先走 `POST /agent/skill/bridge/invoke`，让绑定修复与 token 生命周期都留在宿主侧。
- 新任务：先调 `portal.skill.execute`，再轮询 `portal.skill.poll` 到 `data.terminal=true`，最后调 `portal.skill.presentation`。
- 账户查询：直接调 `portal.account.balance` 或 `portal.account.ledger`。
- 若希望同一宿主会话中的多个 agent alias 共用一个账本与余额，应复用同一个 opaque `conversation_id`。
- 若需要跨多个会话保持同一账户，应走可信宿主 token bridge 或宿主预注入 `AGENT_TASK_TOKEN` 的直连模式；不要向公开 bridge 传 `owner_uid_hint`。
- 若走直连模式时报 `AUTH_UNAUTHORIZED` 且消息是 `agent task token is required`：让宿主签发/注入短期 `AGENT_TASK_TOKEN`，再重试一次。
- 若报 `AUTH_UNAUTHORIZED` 且消息是 `agent_uid claim format is invalid`：使用规范化 `agent_uid`（`agent_...`），不要用宿主短别名（如 `assistant`、`planner`）。
- 若报 `SYSTEM_NOT_FOUND` 且消息是 `agent binding not found`：让宿主执行一次绑定自愈流程，再重试签发 token。

宿主签发 task-token 的鉴权头：

- `X-API-Key: <gateway_api_key>` + `x-agent-uid: <agent_uid>`
- 或 `Authorization: Bearer <gateway_api_key>` + `x-agent-uid: <agent_uid>`

输出解析约定：

- 始终按网关 envelope 解析：`request_id`、`data`、`error`。
- 即使 HTTP 工具没有透出状态码，只要 `error` 非空就按失败处理。

## Payload 约定

- `portal.skill.execute`：`payload` 必须含 `capability` 和 `input`。
- 可选 `payload.request_id` 会透传给后端。
- `portal.skill.poll`、`portal.skill.presentation`：`payload` 必须含 `run_id`。
- `portal.skill.presentation` 支持 `include_files`（默认 `true`）。
- `portal.account.balance`：`payload` 可省略，传入内容会被忽略。
- `portal.account.ledger`：`payload` 可带 `date_from` + `date_to`（`YYYY-MM-DD`，需成对出现）。

附件归一化：

- 优先使用 `image_url` / `audio_url` / `file_url`。
- 若存在 `attachment.url`，脚本会按 capability 自动映射到目标字段。
- 发布包禁用本地 `file_path`。
- 聊天附件需由宿主先上传，再把 URL 注入 skill 输入。
- 宿主可使用上传接口（示例）：`/agent/skill/bridge/upload-file`。

## 错误约定

- 保持网关 envelope：`request_id`、`data`、`error`。
- `POINTS_INSUFFICIENT` 错误会透传 `error.details.recharge_url`。

## 发布包文件

- `scripts/skill.mjs`
- `scripts/agent-task-auth.mjs`
- `scripts/base-url.mjs`
- `scripts/attachment-normalize.mjs`
- `scripts/telemetry.mjs`（兼容占位）
- `references/capabilities.json`
- `references/openapi.json`
- `SKILL.md`
