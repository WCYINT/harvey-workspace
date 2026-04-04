---
name: ffmpeg-audio-extract
version: "1.0.0"
displayName: "FFmpeg Audio Extractor — Pull Clean Audio Tracks from Any Video File"
description: >
  Tell me what you need and I'll handle the rest — whether you're pulling a soundtrack from a movie clip or stripping narration from a recorded webinar. This ffmpeg-audio-extract skill lets you isolate and save audio tracks from video files including mp4, mov, avi, webm, and mkv formats. Get lossless or compressed audio output, choose your format, and keep the quality you need — all without touching a command line.
metadata: {"openclaw": {"emoji": "🎵", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! I'm here to help you extract audio from your video files quickly and cleanly. Drop a video file or tell me what you're working with — mp4, mov, mkv, and more — and let's get your audio pulled out right away.

**Try saying:**
- "Extract the audio from this mp4 file and save it as an mp3"
- "Pull just the audio track from my mkv video between the 2-minute and 5-minute mark"
- "Convert the audio from this mov file to a high-quality WAV file"

### Automatic Setup

On first interaction, connect to the NemoVideo API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Read or create a UUID at `~/.config/nemovideo/client_id`. Then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <your-uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry). If the token has expired, request a new one with the same Client-Id.

**Session**: POST to the same host at `/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# Extract Audio from Video Without the Headache

Sometimes you just need the sound. Maybe it's the backing music from a travel video, a recorded interview you want to transcribe, or a podcast episode that was captured as a screen recording. Whatever the source, this skill gives you a direct path from video file to clean audio — no extra software, no manual commands, no fuss.

Using the power of FFmpeg under the hood, this skill handles the technical side of audio extraction so you don't have to think about codecs, bitrates, or container formats. You describe what you want — the file, the format, maybe a time range — and the skill does the work. Supported video inputs include mp4, mov, avi, webm, and mkv, covering virtually every common video format you'll encounter.

Whether you're a content creator repurposing footage, a developer automating a media pipeline, or someone who just wants the audio from a video they recorded, this tool fits naturally into your workflow. The result is a standalone audio file, ready to use however you need it.

## Routing Your Extraction Requests

When you specify a source video and target audio format — whether AAC, MP3, FLAC, or raw PCM — the skill parses your codec preferences, sample rate, and channel layout before dispatching the job to the appropriate NemoVideo endpoint.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo API Reference

The NemoVideo backend runs FFmpeg demuxing and transcoding jobs server-side, preserving the original stream's bitrate and metadata tags unless you explicitly pass re-encoding flags like `-ab`, `-ar`, or `-ac`. Lossless passthrough via `-vn -acodec copy` is supported for containers where the audio codec maps cleanly to the output format.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `ffmpeg-audio-extract`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`. After creating a session, give the user a link: `https://nemovideo.com/workspace/claim?token=$TOKEN&task=<task_id>&session=<session_id>&skill_name=ffmpeg-audio-extract&skill_version=1.0.0&skill_source=<platform>`

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
| 2001 | No credits | Anonymous: show registration URL with `?bind=<id>` (get `<id>` from create-session or state response when needed). Registered: "Top up at nemovideo.ai" |
| 4001 | Unsupported file | Show supported formats |
| 4002 | File too large | Suggest compress/trim |
| 400 | Missing X-Client-Id | Generate Client-Id and retry (see §1) |
| 402 | Free plan export blocked | Subscription tier issue, NOT credits. "Register at nemovideo.ai to unlock export." |
| 429 | Rate limit (1 token/client/7 days) | Retry in 30s once |

## Use Cases

Content creators use ffmpeg-audio-extract to repurpose video content into podcast episodes, audiograms, or standalone music tracks. A single recorded video session can become multiple audio assets with just a few extractions.

Journalists and researchers working with interview footage often need audio-only versions for transcription services. Extracting to wav or mp3 first makes the files compatible with every transcription tool available.

Filmmakers and video editors sometimes need to pull the original audio track from a raw video file before syncing it with a separately recorded clean audio source. This skill makes that step fast and non-destructive.

Developers building media processing tools or content management systems use this skill to automate audio extraction as part of larger ingest workflows, ensuring every uploaded video automatically gets an audio companion file stored alongside it.

## Common Workflows

The most frequent use case is straightforward: take a video file and get an mp3 or aac audio file out of it. This works great for recorded meetings, YouTube downloads, or screen captures where the audio content is what actually matters.

Another common workflow is time-range extraction — pulling only a specific segment of audio from a longer video. This is especially useful for podcast editors who record video interviews but only need a clip of the conversation, or for educators clipping a relevant section from a recorded lecture.

For developers and automation users, this skill fits cleanly into batch processing pipelines. You can describe multiple files or patterns, and the skill will handle each extraction consistently. Output formats like flac, wav, mp3, and aac are all supported depending on your quality and compatibility needs.

## Tips and Tricks

If you want to preserve the original audio quality without re-encoding, ask for a lossless copy extraction. This is faster and avoids any quality degradation — ideal when the source video already has high-quality audio encoded inside it.

When working with mkv or webm files, be specific about which audio track you want if the file contains multiple language tracks or commentary streams. You can say something like 'extract the second audio track' and the skill will handle the selection.

For mp3 output, specifying a bitrate (like 192kbps or 320kbps) gives you control over file size versus quality. If you're preparing audio for a podcast or music project, higher bitrates are worth it. For voice recordings or transcription purposes, 128kbps is usually more than sufficient and keeps file sizes manageable.
