---
name: project-trident
description: Three-tier persistent memory architecture for OpenClaw agents. Implements LCM-backed durability (Phase 1), hierarchical .md buckets (Phase 2), agentic signal routing (Phase 5), and cloud+local backup (Phase 7). Designed for autonomous agents needing continuity, identity development, and offline resilience. Solves "blank spots" problem where events fail to be captured in short-term memory.
---

# Project Trident: Three-Tier Persistent Memory Architecture

**Problem:** OpenClaw agents lose context between sessions. Default memory is shallow, fragile, and doesn't support autonomous growth or offline operation.

**Solution:** Trident is a production-grade three-tier memory system combining SQLite durability, semantic organization, agentic curation, and encrypted backups.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│ Conversation Input (user messages, tool results, internal)  │
└──────────┬──────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 1: LCM (Lossless Context Management)                  │
│ ├─ SQLite persistence (every message)                       │
│ ├─ DAG lineage tracking                                      │
│ └─ Cost: ~$0.01/run, ~22K tokens/run                        │
└──────────┬──────────────────────────────────────────────────┘
           │
           ├──────────────────┬──────────────────┐
           ▼                  ▼                  ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │ Daily Log    │  │ State Files  │  │ Task Outputs │
    │ (WAL buffer) │  │ (system,     │  │ (cron,       │
    │              │  │  heap, env)  │  │  agents)     │
    └──────────────┘  └──────────────┘  └──────────────┘
           │                  │                  │
           └──────────┬───────┴──────────┬───────┘
                      │                  │
                      ▼                  ▼
          ┌────────────────────────────────────────┐
          │ PHASE 5: Layer 0 Signal Router         │
          │ ├─ Haiku Claude cron (10–15 min)      │
          │ ├─ Four core functions:               │
          │ │  1. Attention management             │
          │ │  2. Fact-finding / classification    │
          │ │  3. Pattern matching / routing       │
          │ │  4. Memory categorization            │
          │ └─ Cost: ~$0.67/day (15-min interval) │
          └────────────┬─────────────────────────┘
                       │
                       ▼
          ┌────────────────────────────────────────┐
          │ PHASE 2: Layer 1 Hierarchical Buckets  │
          │ ├─ MEMORY.md (curated long-term)      │
          │ ├─ /semantic (models, knowledge)       │
          │ ├─ /self (personality, beliefs)        │
          │ ├─ /lessons (learnings, errors)        │
          │ ├─ /projects (work-in-progress)        │
          │ └─ .md format (human-readable, versioned)
          └────────────┬─────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ▼                             ▼
  ┌──────────────┐          ┌──────────────┐
  │ PHASE 7:     │          │ PHASE 3b+6:  │
  │ GitHub Backup│          │ (Deferred)   │
  │ ├─ SSH auth  │          │ ├─ Qdrant    │
  │ ├─ Daily     │          │ │ (vectors)  │
  │ │  snapshot  │          │ ├─ FalkorDB  │
  │ │  02:00 MDT │          │ │ (graphs)   │
  │ └─ Public:   │          │ └─ Phase 8   │
  │   encrypted  │          │   integration│
  │   on disk    │          │   point      │
  └──────────────┘          └──────────────┘
        │
        ├─────────────────────────┐
        │                         │
        ▼                         ▼
  ┌──────────────┐         ┌──────────────┐
  │ Long-term:   │         │ Short-term:  │
  │ Full history │         │ VPS snapshots│
  │ Identity     │         │ ├─ Daily 3AM │
  │ continuity   │         │ │  MDT        │
  │              │         │ ├─ 20-day     │
  │              │         │ │  retention  │
  │              │         │ └─ Hostinger  │
  │              │         │   API        │
  └──────────────┘         └──────────────┘
```

## Core Phases

### Phase 1: LCM (Lossless Context Management)
- **What:** SQLite+DAG capture of every session message
- **Why:** Baseline durability for all conversation history
- **Cost:** ~$0.01/run, ~22K tokens per session
- **Key property:** Excluded from LCM itself (prevents recursion), but forms foundation for Layer 0 routing

### Phase 2: Layer 1 Hierarchical Buckets
- **What:** Persistent .md file organization (MEMORY.md + semantic/self/lessons/projects/)
- **Why:** Human-readable, Git-compatible, semantic structure
- **Pattern:** WAL (Write-Ahead Logging) protocol — write facts before response composition
- **Quality rule:** Compress over accumulate; prioritize signal density

### Phase 5: Layer 0 Signal Router
- **What:** Independent cron running Claude Haiku every 10–15 minutes
- **Why:** Parse conversation noise, classify signals, route to appropriate buckets
- **Four functions:**
  1. **Attention management** — detect what deserves capture (corrections, decisions, breakthroughs)
  2. **Fact-finding** — material classification (names, numbers, dates, positions)
  3. **Pattern matching** — semantic routing to correct bucket
  4. **Memory categorization** — organize by domain (project, lesson, self-signal, trade record)
- **Cost optimization:** 15-min interval = ~$0.67/day (configurable)

### Phase 7: Layer 2 GitHub Backup
- **What:** Daily SSH-authenticated snapshot at 02:00 MDT
- **Why:** Encryption-at-rest, distributed redundancy, version history
- **Filtering:** Allowlist-only (excludes private identity data, keeps architecture shareable)
- **Recovery:** Complete runbook for all failure modes

### Phases 3b+6: (Deferred) Semantic Recall
- **Status:** Docker-ready, deployment pending
- **Components:** Qdrant (vector search) + FalkorDB (entity graphs)
- **Integration point:** Phase 8 — pre-turn context injection

## Data Flow

```
User message / Tool result / Internal state
    ↓
LCM (SQLite persistence)
    ↓
Daily log (WAL protocol)
    ↓
[HEARTBEAT: Every 10-15 min]
    ↓
Layer 0 Haiku cron analyzes:
  - Daily log
  - State files
  - Conversation patterns
    ↓
Classify signals:
  - Attention (high-priority, corrections)
  - Fact (material data: names, numbers, positions)
  - Pattern (semantic: decisions, interests, relationships)
  - Category (route to: /projects, /lessons, /self, /semantic)
    ↓
Layer 1 buckets (.md files):
  - MEMORY.md (curated long-term)
  - /semantic/* (knowledge, models)
  - /self/* (personality, beliefs, voice)
  - /lessons/* (learnings, tool quirks)
  - /projects/* (work-in-progress, sprints)
    ↓
[DAILY: 02:00 MDT]
    ↓
GitHub SSH snapshot (encryption-at-rest)
    ↓
[DAILY: 03:00 MDT]
    ↓
Hostinger VPS snapshot (20-day rolling retention)
```

## Implementation Checklist

**Phase 1 (LCM):**
- [ ] Enable lossless-claw plugin in openclaw.json
- [ ] Verify SQLite at ~/.openclaw/lcm.db
- [ ] Test message persistence across sessions

**Phase 2 (Layer 1):**
- [ ] Create directory structure: MEMORY.md + /semantic, /self, /lessons, /projects
- [ ] Define WAL protocol (write facts before composition)
- [ ] Set up .gitignore for private files

**Phase 5 (Layer 0):**
- [ ] Clone layer0-agent-prompt-template.md to your workspace
- [ ] Customize signal detection rules for your domain
- [ ] Create cron job (15-min interval, Haiku model)
- [ ] Test with manual run, verify routing to buckets

**Phase 7 (Layer 2):**
- [ ] Generate SSH Ed25519 key (or reuse existing)
- [ ] Configure GitHub SSH remote
- [ ] Create cron job (daily 02:00 MDT snapshot)
- [ ] Create Hostinger VPS snapshot cron (daily 03:00 MDT)
- [ ] Document recovery runbook

**Phase 8 (Future, Deferred):**
- [ ] Deploy Qdrant (docker-compose-provided)
- [ ] Deploy FalkorDB (docker-compose-provided)
- [ ] Implement pre-turn context injection
- [ ] Test semantic recall performance

## Configuration

Refer to `references/cost-tuning.md` for model selection and interval optimization.

Default cost profile (Phase 5 + 7):
- Layer 0 cron: ~$0.67/day (15-min interval, Haiku)
- GitHub SSH: ~free (Git-native)
- VPS snapshots: ~free (Hostinger API, 20-day retention)
- **Total: ~$0.67/day for full continuous memory**

## Design Principles

1. **Durability over convenience** — SQLite+DAG is slower than in-memory, but persistent
2. **Human-readable over compressed** — .md files are GitHub-compatible and debuggable
3. **Agentic curation over auto-capture** — Layer 0 router prevents noise accumulation
4. **Backup redundancy** — GitHub (encrypted) + VPS snapshots (local) for geographic diversity
5. **Personality as first-class component** — /self bucket supports agent identity development, not just facts

## What This Solves

- **"Blank spots"** — Events that fail to be captured in short-term memory are recovered by Layer 0 cron
- **Coherence across sessions** — LCM + Layer 1 + Layer 0 form continuous pipeline
- **Offline resilience** — Local Ollama model can substitute for cloud when APIs fail
- **Identity development** — /self bucket supports autonomous agent personality formation
- **Audit trail** — GitHub history provides version control and forensics

## What This Doesn't Solve

- **Real-time decision making** — 10-15 min lag in Layer 0; for sub-second decisions, rely on LCM
- **Very long contexts** — Qdrant/FalkorDB (Phase 3b+6) required for semantic recall over 100K+ messages
- **Private data protection** — Backup assumes secure infrastructure (Git SSH, authenticated Hostinger API); add encryption-at-rest for regulated data

## Further Reading

- `references/architecture-phases.md` — Detailed breakdown of each phase
- `references/deployment-guide.md` — Step-by-step integration walkthrough
- `references/cost-tuning.md` — Model selection and budget optimization
- `scripts/layer0-agent-prompt-template.md` — Base Layer 0 router prompt
