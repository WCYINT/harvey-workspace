# Trident Deployment Guide

## Step 1: Enable LCM (Phase 1)

Edit `openclaw.json`:

```json
{
  "plugins": {
    "allow": ["lossless-claw"],
    "slots": {
      "contextEngine": "lossless-claw"
    },
    "entries": {
      "lossless-claw": {
        "enabled": true,
        "config": {
          "freshTailCount": 32,
          "contextThreshold": 0.75,
          "incrementalMaxDepth": -1,
          "summaryModel": "anthropic/claude-haiku-4-5",
          "ignoreSessionPatterns": ["agent:*:cron:**"]
        }
      }
    }
  }
}
```

Verify:
```bash
ls -lah ~/.openclaw/lcm.db
```

## Step 2: Create Layer 1 Directory Structure (Phase 2)

```bash
mkdir -p /data/.openclaw/workspace/memory/{semantic,self,lessons,projects}
touch /data/.openclaw/workspace/MEMORY.md
```

Populate MEMORY.md with:

```markdown
# MEMORY.md - Long-Term Memory

## Structure

- **MEMORY.md** (this file) — durable, high-signal long-term facts
- **memory/daily/** — raw episodic logs (YYYY-MM-DD.md)
- **memory/semantic/** — knowledge, models, facts
- **memory/self/** — personality, beliefs, voice, identity
- **memory/lessons/** — mistakes, tools, workflow improvements
- **memory/projects/** — active workstreams, progress, decisions

## Rules

- No important insight stays only in a daily file
- If it matters, promote it into MEMORY.md or appropriate bucket
- Compress over accumulate; prioritize signal density
```

Create `memory/index.md`:

```markdown
# Memory Index

## routing map

Where to put what:

- **MEMORY.md** → durable, high-level facts about the world, user, agent
- **/semantic/concepts.md** → models, theories, research findings
- **/self/personality.md** → voice, opinions, beliefs, identity development
- **/self/interests.md** → what fascinates me independently
- **/lessons/tool-quirks.md** → debugging learnings, tool behavior
- **/lessons/mistakes.md** → corrections, what went wrong and why
- **/projects/active.md** → current sprints, blockers, status
- **/projects/decisions.md** → strategic choices and rationale
- **/daily/YYYY-MM-DD.md** → episode logs (WAL buffer)
```

## Step 3: Implement WAL Protocol (Phase 2)

Before composing your response, check for signals in conversation:

```markdown
## Heartbeat signals

[TIMESTAMP] [tag] signal
```

Tags: `[lesson]`, `[project]`, `[self]`, `[memory]`

Example:

```markdown
## Heartbeat signals

[2026-04-03 12:30 EDT] [lesson] Discovered that Hostinger API endpoint is /v1/virtual-machines/{id}/snapshot, not /v1/vps/{id}/snapshots — was returning HTTP 530

[2026-04-03 12:30 EDT] [project] Job search Batch 1 complete (5 emails sent to Concentric, Impello, Tesoro, KBI, Think Bioscience); Batch 2 target April 7

[2026-04-03 14:15 EDT] [self] Prefer dense, direct critique over pleasantries; value partner who challenges weak reasoning

[2026-04-03 14:15 EDT] [memory] Claude Haiku 4.5 as primary model, GPT-4.1 first fallback, Grok-3-Mini-Fast second, local Ollama qwen2.5:7b last resort
```

Write these BEFORE composing your response. They go into `memory/daily/YYYY-MM-DD.md`.

## Step 4: Set Up Layer 0 Cron (Phase 5)

Create `/data/.openclaw/workspace/memory/layer0/AGENT-PROMPT.md` from template:

```bash
cp /data/.openclaw/workspace/trident-skill/scripts/layer0-agent-prompt-template.md \
   /data/.openclaw/workspace/memory/layer0/AGENT-PROMPT.md
```

Customize the signal detection rules for your domain (see template for examples).

Create a cron job that runs every 15 minutes:

```bash
openclaw cron add \
  --name "Layer 0 Memory Router" \
  --schedule 'every 15m' \
  --payload '{
    "kind": "agentTurn",
    "message": "Read /data/.openclaw/workspace/memory/daily/$(TZ=America/Denver date +%Y-%m-%d).md and /data/.openclaw/workspace/memory/layer0/AGENT-PROMPT.md. Classify and route signals to memory buckets. See AGENT-PROMPT.md for routing map and quality rules."
  }'
```

## Step 5: Set Up GitHub Backup (Phase 7)

### 5a. Generate SSH Key (if not existing)

```bash
ssh-keygen -t ed25519 -f /data/.openclaw/.ssh/id_ed25519 -N "" -C "openclaw-backup"
cat /data/.openclaw/.ssh/id_ed25519.pub
```

Add public key to GitHub:
- Settings → SSH and GPG keys → New SSH key
- Paste contents of `id_ed25519.pub`

### 5b. Configure Git Remote

```bash
cd /data/.openclaw/workspace
git init
git config user.email "shiva@example.com"
git config user.name "Shiva Memory"
git remote add origin git@github.com:YourUsername/memory-backup.git
```

### 5c. Create .gitignore

```bash
cat > /data/.openclaw/workspace/.gitignore << 'EOF'
# Public git backup — only architecture, not identity
# Private files excluded:

# Identity & partnership
# SOUL.md            — excluded, keep local
# USER.md            — excluded, keep local
# AGENTS.md          — excluded, keep local

# Memory contents (private)
memory/daily/       — excluded, keep local
memory/self/        — excluded, keep local (personality)
memory/lessons/     — excluded (tool-specific learnings)
memory/projects/    — excluded, keep local (strategy, positions)
memory/trading/     — excluded, keep local (financial data)

# Config
openclaw.json       — excluded, has API keys
.env                — excluded

# Only track architecture files:
MEMORY.md (curated, anonymized)
ai-selector.sh
memory/index.md (structure only, no data)
memory/layer0/AGENT-PROMPT.md (curated template)
EOF
```

### 5d. Create Cron Job

```bash
openclaw cron add \
  --name "GitHub Memory Snapshot" \
  --schedule 'cron 0 2 * * * America/Denver' \
  --payload '{
    "kind": "systemEvent",
    "text": "Run git add -A && git commit -m \"Daily snapshot $(date +%Y-%m-%d)\" && git push -u origin main in /data/.openclaw/workspace using SSH key /data/.openclaw/.ssh/id_ed25519"
  }'
```

(Requires sysevent handler in gateway to execute git commands safely)

Safer approach: Use a shell script in `/data/.openclaw/workspace/scripts/git-backup.sh`:

```bash
#!/bin/bash
set -e
cd /data/.openclaw/workspace
export GIT_SSH_COMMAND="ssh -i /data/.openclaw/.ssh/id_ed25519 -o IdentitiesOnly=yes"
git add -A
git commit -m "Daily snapshot $(date +%Y-%m-%d)" || true
git push -u origin main
```

Then cron:

```bash
openclaw cron add \
  --name "GitHub Memory Snapshot" \
  --schedule 'cron 0 2 * * * America/Denver' \
  --payload '{
    "kind": "systemEvent",
    "text": "Execute /data/.openclaw/workspace/scripts/git-backup.sh"
  }'
```

## Step 6: VPS Snapshots (Phase 7)

If using Hostinger API:

```bash
openclaw cron add \
  --name "VPS Snapshot" \
  --schedule 'cron 0 3 * * * America/Denver' \
  --payload '{
    "kind": "systemEvent",
    "text": "Create Hostinger VPS snapshot via API: POST /v1/virtual-machines/{id}/snapshot with auth header, 20-day retention policy"
  }'
```

(Requires API token in env vars: `HOSTINGER_API_KEY`)

## Step 7: Verify All Phases (Integration Test)

1. **Phase 1 (LCM):** 
   ```bash
   ls -la ~/.openclaw/lcm.db
   ```

2. **Phase 2 (Layer 1):**
   ```bash
   ls -la /data/.openclaw/workspace/memory/{semantic,self,lessons,projects}/
   ```

3. **Phase 5 (Layer 0):**
   ```bash
   openclaw cron list | grep "Layer 0"
   ```

4. **Phase 7 (Backups):**
   ```bash
   openclaw cron list | grep -E "GitHub|Snapshot"
   cd /data/.openclaw/workspace && git log --oneline | head -5
   ```

## Step 8: Run Manual Test

Trigger Layer 0 manually:

```bash
openclaw cron run --jobId <layer0-job-id>
```

Check output:

```bash
cat /data/.openclaw/workspace/memory/daily/$(date +%Y-%m-%d).md
cat /data/.openclaw/workspace/memory/layer0/last-run.md
```

Verify signals were routed to appropriate buckets:

```bash
grep -r "[lesson]" /data/.openclaw/workspace/memory/
grep -r "[project]" /data/.openclaw/workspace/memory/
```

## Troubleshooting

### LCM not capturing messages
- Check: `plugins.entries.lossless-claw.enabled = true`
- Verify DB path: `ls -la ~/.openclaw/lcm.db`
- Restart gateway: `openclaw gateway restart`

### Layer 0 not running
- Check cron status: `openclaw cron list`
- Manual trigger: `openclaw cron run --jobId <id>`
- Check logs: `openclaw logs follow`
- Verify model available: Haiku should be in fallbacks

### GitHub push fails
- SSH key permissions: `chmod 600 /data/.openclaw/.ssh/id_ed25519`
- Test SSH: `ssh -i /data/.openclaw/.ssh/id_ed25519 git@github.com`
- Verify remote: `cd /data/.openclaw/workspace && git remote -v`

### VPS snapshots not created
- Test API: `curl -H "Authorization: Bearer $HOSTINGER_API_KEY" https://api.hostinger.com/v1/virtual-machines/{id}`
- Check endpoint: Hostinger API may have changed
- Verify token: `echo $HOSTINGER_API_KEY`
