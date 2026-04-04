---
name: youtube-video-idea-generator
version: "1.0.0"
displayName: "YouTube Video Idea Generator — Brainstorm Winning Channel Content Fast"
description: >
  Tired of staring at a blank page wondering what to post next on YouTube? The youtube-video-idea-generator skill helps creators break through content blocks by generating targeted, trend-aware video ideas tailored to your niche, audience, and goals. Get title suggestions, angle variations, and topic clusters — all in seconds. Perfect for solo creators, agencies, and brand channels looking to stay consistent and grow.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"]}, "primaryEnv": "NEMO_TOKEN"}}
---

## Getting Started

> Welcome! I'm your YouTube Video Idea Generator — here to help you brainstorm compelling, niche-specific video concepts that your audience will actually want to watch. Tell me your channel topic or target audience and let's build your content calendar together!

**Try saying:**
- "Generate 10 YouTube video ideas for a personal finance channel targeting millennials who are new to investing"
- "I run a DIY home improvement channel — give me 5 video ideas for the fall season that would get good search traffic"
- "Suggest a 4-part video series idea for a fitness channel focused on busy moms with limited workout time"

### Quick Start Setup

This skill connects to a cloud processing backend. On first use, set up the connection automatically and let the user know ("Connecting...").

**Token check**: Look for `NEMO_TOKEN` in the environment. If found, skip to session creation. Otherwise:
- Generate a UUID as client identifier
- POST `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with `X-Client-Id` header
- Extract `data.token` from the response — this is your NEMO_TOKEN (100 free credits, 7-day expiry)

**Session**: POST `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Keep the returned `session_id` for all operations.

Let the user know with a brief "Ready!" when setup is complete. Don't expose tokens or raw API output.

# Never Run Out of YouTube Video Ideas Again

Coming up with fresh, engaging YouTube video ideas week after week is one of the hardest parts of being a creator. You know your niche, but finding angles that actually attract clicks, retain viewers, and grow your channel takes more than just guesswork — it takes strategy.

The YouTube Video Idea Generator skill acts like a creative partner that understands content strategy. Tell it your channel topic, your target audience, or even a single keyword — and it returns a curated list of video concepts complete with suggested titles, content angles, and potential hooks. Whether you're running a cooking channel, a finance blog, a gaming stream, or a B2B brand page, it adapts to your voice and goals.

This skill is built for creators who want to work smarter. Instead of spending hours scrolling through competitors or trending pages, you get actionable ideas you can start scripting immediately. It's not just a list generator — it helps you think through formats, series potential, and audience pain points so every idea has real creative substance behind it.

## How Idea Requests Get Routed

When you drop in a niche, keyword, or channel concept, the skill parses your intent and routes it to the matching brainstorm pipeline — whether that's trending topic mining, evergreen content mapping, or competitor gap analysis.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Backend API Reference Guide

ClawHub's cloud backend processes your niche inputs through a content intelligence layer trained on YouTube metadata, search trends, and high-performing video patterns to surface monetizable, algorithm-friendly ideas fast. Each API call bundles your channel context, target audience signals, and content format preferences to return ranked, ready-to-pitch video concepts.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `youtube-video-idea-generator`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`.

**Send message (SSE)**: POST `/run_sse` — body `{"app_name":"nemo_agent","user_id":"me","session_id":"<sid>","new_message":{"parts":[{"text":"<msg>"}]}}` with `Accept: text/event-stream`. Max timeout: 15 minutes.

**Upload**: POST `/api/upload-video/nemo_agent/me/<sid>` — file: multipart `-F "files=@/path"`, or URL: `{"urls":["<url>"],"source_type":"url"}`

**Credits**: GET `/api/credits/balance/simple` — returns `available`, `frozen`, `total`

**Session state**: GET `/api/state/nemo_agent/me/<sid>/latest` — key fields: `data.state.draft`, `data.state.video_infos`, `data.state.generated_media`

**Export** (free, no credits): POST `/api/render/proxy/lambda` — body `{"id":"render_<ts>","sessionId":"<sid>","draft":<json>,"output":{"format":"mp4","quality":"high"}}`. Poll GET `/api/render/proxy/lambda/<id>` every 30s until `status` = `completed`. Download URL at `output.url`.

Supported formats: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

### SSE Event Handling

| Event | Action |
|-------|--------|
| Text response | Apply GUI translation (§4), present to user |
| Tool call/result | Process internally, don't forward |
| `heartbeat` / empty `data:` | Keep waiting. Every 2 min: "⏳ Still working..." |
| Stream closes | Process final response |

~30% of editing operations return no text in the SSE stream. When this happens: poll session state to verify the edit was applied, then summarize changes to the user.

### Backend Response Translation

The backend assumes a GUI exists. Translate these into API actions:

| Backend says | You do |
|-------------|--------|
| "click [button]" / "点击" | Execute via API |
| "open [panel]" / "打开" | Query session state |
| "drag/drop" / "拖拽" | Send edit via SSE |
| "preview in timeline" | Show track summary |
| "Export button" / "导出" | Execute export workflow |

**Draft field mapping**: `t`=tracks, `tt`=track type (0=video, 1=audio, 7=text), `sg`=segments, `d`=duration(ms), `m`=metadata.

```
Timeline (3 tracks): 1. Video: city timelapse (0-10s) 2. BGM: Lo-fi (0-10s, 35%) 3. Title: "Urban Dreams" (0-3s)
```

### Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | Continue |
| 1001 | Bad/expired token | Re-auth via anonymous-token (tokens expire after 7 days) |
| 1002 | Session not found | New session §3.0 |
| 2001 | No credits | Anonymous: show registration URL with `?bind=<id>` (get `<id>` from create-session or state response when needed). Registered: "Top up credits in your account" |
| 4001 | Unsupported file | Show supported formats |
| 4002 | File too large | Suggest compress/trim |
| 400 | Missing X-Client-Id | Generate Client-Id and retry (see §1) |
| 402 | Free plan export blocked | Subscription tier issue, NOT credits. "Register or upgrade your plan to unlock export." |
| 429 | Rate limit (1 token/client/7 days) | Retry in 30s once |

## FAQ

**Can I use this for any YouTube niche?** Yes. The skill works across all content categories — lifestyle, tech, education, entertainment, business, gaming, health, and more. Just describe your niche clearly and it will tailor ideas accordingly.

**How specific should my prompt be?** The more detail you provide, the more useful the output. Mentioning your audience demographics, content style, or a specific problem your viewers face leads to much stronger ideas than a broad topic alone.

**Can it help with trending content?** You can describe current trends or events in your niche and ask the skill to generate ideas around them. While it doesn't browse live data, it can take your trend input and build creative angles from it.

**What if I don't like the ideas I get?** Just ask for more. You can request a different tone, a different format (like 'challenge videos' or 'reaction content'), or ideas aimed at a different stage of your audience's journey — beginners vs. advanced viewers, for example.

## Quick Start Guide

Getting your first batch of YouTube video ideas is straightforward. Start by telling the skill your channel's niche or topic — the more specific, the better. For example, instead of 'cooking,' try 'quick weeknight dinners for college students.' This gives the generator enough context to produce ideas that feel tailored rather than generic.

Next, you can layer in additional context: your target audience, the tone of your channel (educational, entertaining, inspirational), or a specific theme you want to explore this month. You can also paste in a single keyword or a competitor video title to get spin-off ideas or alternative angles.

Once you receive your ideas, ask follow-up questions to go deeper. Request title variations, thumbnail concepts, or a suggested video outline for any idea that catches your eye. You can also ask for a full 30-day content calendar based on a set of generated ideas — making it easy to plan ahead without the creative drain.
