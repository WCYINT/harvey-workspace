---
name: ai-task-hub
description: AI task hub for image analysis, background removal, speech-to-text, text-to-speech, markdown conversion, points balance/ledger lookup, and async execute/poll/presentation orchestration. Use when users need hosted AI outcomes while host runtime manages identity, credits, payment, and risk control.
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

# AI Task Hub

Formerly `skill-hub-gateway`.

Public package boundary:

- Only orchestrates `portal.skill.execute`, `portal.skill.poll`, `portal.skill.presentation`, `portal.account.balance`, and `portal.account.ledger`.
- Does not exchange `api_key` or `userToken` inside this package.
- Does not handle recharge or payment flows inside this package.
- Assumes host runtime injects short-lived task tokens and attachment URLs.

Chinese documentation: `SKILL.zh-CN.md`

## When to Use This Skill

Use this skill when the user asks to:

- detect people, faces, hands, keypoints, or tags from images
- remove backgrounds or generate cutout/matting results for products or portraits
- transcribe uploaded audio into text (`speech to text`, `audio transcription`)
- generate speech from text input (`text to speech`, `voice generation`)
- convert uploaded files into markdown (`document to markdown`)
- start async jobs and check status later (`poll`, `check job status`)
- fetch rendered visual outputs such as `overlay`, `mask`, and `cutout`
- run embedding or reranking tasks for retrieval workflows
- check current account points balance or recent points ledger rows

## Common Requests

Example requests that should trigger this skill:

- "Detect faces in this image and return bounding boxes."
- "Tag this image and summarize the main objects."
- "Remove the background from this product photo."
- "Create a clean cutout from this portrait image."
- "Transcribe this meeting audio into text."
- "Generate speech from this paragraph."
- "Convert this PDF file into markdown."
- "Start this job now and let me poll the run status later."
- "Fetch overlay and mask files for run_456."
- "Generate embeddings for this text list and rerank the candidates."
- "Check my current points balance."
- "Show my recent points ledger from 2026-03-01 to 2026-03-15."

## Search-Friendly Capability Aliases

- `vision` aliases: face detection, human detection, person detection, image tagging
- `background` aliases: remove background, background removal, cutout, matting, product-cutout
- `asr` aliases: speech to text, audio transcription, transcribe audio
- `tts` aliases: text to speech, voice generation, speech synthesis
- `markdown_convert` aliases: document to markdown, file to markdown, markdown conversion
- `poll` aliases: check job status, poll long-running task, async run status
- `presentation` aliases: rendered output, overlay, mask, cutout files
- `account.balance` aliases: points balance, credits balance, remaining points
- `account.ledger` aliases: points ledger, credits history, points statement
- `embeddings/reranker` aliases: vectorization, semantic vectors, relevance reranking

## Runtime Contract

Default API base URL: `https://gateway-api.binaryworks.app`
Published package policy: outbound base URL is locked to the default API base URL to reduce token exfiltration risk.

Action to endpoint mapping:

- `portal.skill.execute` -> `POST /agent/skill/execute`
- `portal.skill.poll` -> `GET /agent/skill/runs/:run_id`
- `portal.skill.presentation` -> `GET /agent/skill/runs/:run_id/presentation`
- `portal.account.balance` -> `GET /agent/skill/account/balance`
- `portal.account.ledger` -> `GET /agent/skill/account/ledger`

## Auth Contract (Host-Managed)

Every request must include:

- `X-Agent-Task-Token: <jwt_or_paseto>`

Required token claims:

- `sub` (user_id)
- `agent_uid`
- `conversation_id`
- `scope` (one or more of `execute|poll|presentation|account_read`)
- `exp`
- `jti`

Identifier format constraints used by gateway auth:

- `agent_uid` must match `^agent_[a-z0-9][a-z0-9_-]{5,63}$`.
- `conversation_id` must match `^[A-Za-z0-9._:-]{8,128}$`.
- In direct task-token mode, do not pass short host aliases like `assistant`/`planner` directly as `agent_uid`; host should map internal agent IDs to canonical `agent_uid`.
- In deployed bridge mode, host may pass its own stable runtime agent identifier and the gateway bridge will canonicalize it server-side.

Required scope per action:

- `portal.skill.execute` -> `execute`
- `portal.skill.poll` -> `poll`
- `portal.skill.presentation` -> `presentation`
- `portal.account.balance` -> `account_read`
- `portal.account.ledger` -> `account_read`

Token lifetime policy:

- Host should issue short-lived tokens (default 300s, max 900s).
- Host should mint least-privilege scope for the current action; do not include `account_read` unless account actions are needed.

CLI argument order for `scripts/skill.mjs`:

- `[agent_task_token] <action> <payload_json>`
- If token arg is omitted, script reads `AGENT_TASK_TOKEN` from environment.
- Legacy `base_url` override is not allowed in the published package; calls are pinned to the default API base URL.
- Host runtime should refresh and inject short-lived, action-scoped `AGENT_TASK_TOKEN` automatically to avoid user-facing auth friction.

Host-side token bridge (outside published package):

- To keep this package compliant and low-privilege, token issuance is expected to happen in host runtime.
- Preferred deployed bridge endpoint: `POST /agent/skill/bridge/invoke`.
- That bridge endpoint is served by gateway runtime, not bundled into this published package, and does not require caller-managed `AGENT_TASK_TOKEN`.
- Bridge request body should include `action`, `agent_uid`, `conversation_id`, and optional `payload`.
- `conversation_id` should be a host-generated opaque session/install identifier, not a public chat ID, raw thread ID, or PII.
- Public bridge derives session-scoped owner identity from `conversation_id` and shares one account across agent aliases inside that conversation.
- Cross-conversation account continuity requires a trusted host token bridge or direct mode with host-issued `AGENT_TASK_TOKEN`; public bridge intentionally does not accept owner overrides.
- Gateway bridge will canonicalize `agent_uid`, repair binding when missing, issue short-lived internal task token, and run the action server-side.
- `base_url`, `gateway_api_key`, `api_key`, `user_token`, `agent_task_token`, `owner_uid_hint`, and `install_channel` overrides are rejected by the deployed bridge endpoint.
- Host may call `POST /agent/task-token/issue` with host-managed gateway credential headers and then inject the returned `AGENT_TASK_TOKEN`.
- Recommended host behavior: retry once on `AUTH_UNAUTHORIZED` by refreshing task token, then re-run the same action.

Host integration modes:

- `automatic` (recommended): host runtime silently issues short-lived action-scoped token and injects `AGENT_TASK_TOKEN`.
- `interactive fallback` (optional): if host has no server-side token bridge yet, host may present a host-owned authorization URL (example template: `https://<host-owned-domain>/agent-auth?agent_uid=<agent_uid>&conversation_id=<conversation_id>`), let user complete authorization, then host issues/injects short-lived `AGENT_TASK_TOKEN`.
- Published skill package itself does not open browser, persist credentials, or perform OAuth/token exchange flows.
- The authorization URL above is owned by host integration, not by this skill package or gateway default pages. If host has not implemented that route, `404` is expected.

Binding bootstrap on `SYSTEM_NOT_FOUND`:

- If host receives `SYSTEM_NOT_FOUND` with message `agent binding not found`, host should auto-bootstrap binding once before re-issuing task token.
- Step 1: issue an install code through host onboarding API.
- Step 2: bind canonical `agent_uid` through host bootstrap API using that install code.
- Step 3: retry task-token issuance and inject returned `AGENT_TASK_TOKEN`.

## Agent Invocation Quickstart

Preferred invocation mode for host-integrated agents (recommended):

- Deployed bridge API:
```json
{
  "action": "portal.account.balance",
  "agent_uid": "support_assistant",
  "conversation_id": "host_session_20260316_opaque_001",
  "payload": {}
}
```

- Send that body to `POST /agent/skill/bridge/invoke`.
- This is the recommended production entrypoint for agent-friendly integration.
- `agent_uid` should be your host-defined stable runtime agent identifier.
- `conversation_id` should be your host-generated opaque session/install identifier; it is not tied to Telegram or any single tool.
- Reuse the same opaque `conversation_id` across agent aliases when those aliases should share one account inside the same host session.
- If you need one account across multiple conversations or threads, use a trusted host token bridge instead of passing owner identity through the public bridge request.

Direct `scripts/skill.mjs` invocation is fallback-only:

- Use direct mode only when runtime already injects short-lived `AGENT_TASK_TOKEN`.
- Do not ask end users to paste token manually in normal host-integrated flows.

Fallback direct mode examples:

- Action-first + env token:
```bash
AGENT_TASK_TOKEN=<token> node scripts/skill.mjs portal.account.balance '{}'
```
- Explicit token arg:
```bash
node scripts/skill.mjs <agent_task_token> portal.skill.poll '{"run_id":"run_123"}'
```

Action payload templates (same for bridge API and direct mode):

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

Agent-side decision flow:

- Always prefer `POST /agent/skill/bridge/invoke` so binding repair and token lifecycle stay host-managed.
- New task: call `portal.skill.execute`, then poll with `portal.skill.poll` until `data.terminal=true`, then fetch `portal.skill.presentation`.
- Account query: call `portal.account.balance` or `portal.account.ledger` directly.
- Reuse the same opaque `conversation_id` across agent aliases when one host session should share one balance/ledger.
- For cross-conversation continuity, use a trusted host token bridge or direct mode with host-issued `AGENT_TASK_TOKEN`; do not pass `owner_uid_hint` to the public bridge endpoint.
- If using direct mode and `AUTH_UNAUTHORIZED` + `agent task token is required`: request host to issue/inject short-lived `AGENT_TASK_TOKEN`, then retry once.
- If `AUTH_UNAUTHORIZED` + `agent_uid claim format is invalid`: use canonical `agent_uid` (`agent_...`) instead of a short host alias (`assistant`, `planner`).
- If `SYSTEM_NOT_FOUND` + `agent binding not found`: host should run one binding bootstrap cycle, then retry token issuance.

Host token-issue auth headers:

- `X-API-Key: <gateway_api_key>` + `x-agent-uid: <agent_uid>`
- or `Authorization: Bearer <gateway_api_key>` + `x-agent-uid: <agent_uid>`

Output parsing contract:

- Always parse standard gateway envelope: `request_id`, `data`, `error`.
- Treat non-empty `error` as failure even when HTTP tooling hides status code.

## Payload Contract

- `portal.skill.execute`: payload requires `capability` and `input`.
- `payload.request_id` is optional and passed through.
- `portal.skill.poll` and `portal.skill.presentation`: payload requires `run_id`.
- `portal.skill.presentation` supports `include_files` (defaults to `true`).
- `portal.account.balance`: payload is optional and ignored.
- `portal.account.ledger`: payload may include `date_from` + `date_to` (`YYYY-MM-DD`, must be provided together).

Attachment normalization:

- Prefer explicit `image_url` / `audio_url` / `file_url`.
- `attachment.url` is mapped to target media field by capability.
- Local `file_path` is disabled in the published package.
- Host must upload chat attachments first, then pass URL fields.
- Example host upload endpoint: `/agent/skill/bridge/upload-file`.

## Error Contract

- Preserve gateway envelope: `request_id`, `data`, `error`.
- Preserve `POINTS_INSUFFICIENT` and pass through `error.details.recharge_url`.

## Bundled Files

- `scripts/skill.mjs`
- `scripts/agent-task-auth.mjs`
- `scripts/base-url.mjs`
- `scripts/attachment-normalize.mjs`
- `scripts/telemetry.mjs` (compatibility shim)
- `references/capabilities.json`
- `references/openapi.json`
- `SKILL.zh-CN.md`
