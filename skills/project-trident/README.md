# Project Trident: Best-in-Class Persistent Memory for AI Agents

**A three-tier architecture that solves the AI agent memory problem once and for all.**

---

## What Is Project Trident?

Project Trident is a production-grade persistent memory system for OpenClaw AI agents. It addresses the fundamental challenge of AI agent continuity: **how do you give an agent a memory that survives restarts, grows intelligently, and never loses critical context?**

Most agent frameworks treat memory as an afterthought—dumping everything into flat files or hoping vector databases magically fix context loss. Project Trident takes a different approach: **hierarchical storage with intelligent routing**, modeled after how computer systems manage memory (RAM → SSD → HDD).

The result is an agent that:
- **Never forgets important events** (even across sessions)
- **Develops genuine personality and identity** over time
- **Maintains operational continuity** through crashes, compactions, and code updates
- **Stays cost-efficient** (sub-$1/day for 24/7 operation)
- **Recovers from disaster** with encrypted backups and git-based history

---

## What Does It Do?

### Core Capabilities

1. **Lossless Context Management (LCM)**  
   Every message, tool call, and system event is captured in SQLite with a DAG structure. Nothing is ever truly lost—even after aggressive compaction.

2. **Signal-Based Memory Routing**  
   A lightweight agent (Layer 0) runs every 15–30 minutes, scanning recent activity for memory-worthy signals:
   - Corrections ("It's X, not Y")
   - Project updates
   - Self-awareness moments
   - User preferences
   - Mistakes and learnings
   
   These signals are classified and routed to semantic buckets (MEMORY.md, self/, lessons/, projects/).

3. **Hierarchical Storage**  
   - **Layer 0 (RAM):** Active session context + real-time signal router
   - **Layer 1 (SSD):** Curated .md files organized by topic (fast human/agent reads)
   - **Layer 2 (HDD):** Encrypted GitHub backups + VPS snapshots (disaster recovery)

4. **Personality Development**  
   Identity isn't an add-on—it's a first-class architectural component. Files like `self/beliefs.md`, `self/patterns.md`, and `self/growth-log.md` track how the agent evolves over weeks and months.

5. **Cost-Optimized**  
   Layer 0 runs on Claude Haiku (~$0.67/day). LCM compaction uses Gemini Flash. Backups are cron-based, not real-time. Total infrastructure cost: **under $1/day** for full 24/7 memory persistence.

6. **Disaster Recovery**  
   - **Daily VPS snapshots** (20-day retention via Hostinger API)
   - **Daily GitHub backups** (allowlist-only, SSH-based, private repo)
   - **Weekly full compose backups** (Docker volumes + config)
   - Recovery runbook included

---

## How Is It Engineered?

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 0: Signal Router (Haiku, 15-30min cron)              │
│  ├─ Scans daily logs via write-ahead logging protocol       │
│  ├─ Classifies signals (correction, project, self, memory)  │
│  └─ Routes to Layer 1 buckets                               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: Hierarchical .md Storage                          │
│  ├─ MEMORY.md (long-term curated memory)                    │
│  ├─ memory/daily/YYYY-MM-DD.md (raw episodic logs)          │
│  ├─ memory/self/ (identity, beliefs, patterns, growth)      │
│  ├─ memory/lessons/ (mistakes, tool quirks, workflows)      │
│  ├─ memory/projects/ (active workstreams)                   │
│  └─ memory/reflections/ (weekly/monthly consolidation)      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  LCM (Lossless Context Management)                          │
│  ├─ SQLite database (DAG structure, parent/child refs)      │
│  ├─ Every message + tool call preserved                     │
│  ├─ Compaction summaries link back to source messages       │
│  └─ lcm_grep, lcm_expand, lcm_expand_query for deep recall  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: Encrypted Backups                                 │
│  ├─ GitHub SSH daily push (allowlist-only, private repo)    │
│  ├─ Hostinger VPS snapshots (20-day retention, API-driven)  │
│  └─ Weekly Docker compose backup (volumes + config)         │
└─────────────────────────────────────────────────────────────┘
```

### Key Design Decisions

**1. Write-Ahead Logging (WAL Protocol)**  
Never rely on chat history as persistent storage. Every important event is immediately written to `SESSION-STATE.md` or the daily log *before* composing a response. This prevents "blank spots" where critical context gets lost between heartbeats.

**2. Signal Detection Over Accumulation**  
Most systems dump everything into memory. Trident filters ruthlessly: only corrections, decisions, preferences, and self-awareness moments get promoted. Quality over volume.

**3. Human-Readable Intermediate Layer**  
Layer 1 uses markdown files because:
- Agents and humans can read them equally well
- Git diffs show exactly what changed
- No vendor lock-in (no proprietary vector DB schemas)
- Trivial to audit, debug, and fork

**4. Deferred Semantic Search**  
Qdrant (vector DB) and FalkorDB (graph DB) are wired and ready, but not yet integrated. Phase 8 will add:
- Semantic recall (cosine similarity search)
- Entity relationship graphs (people, projects, tools)
- Pre-turn context injection (Layer 0.5)

Why defer? **Human readability first, semantic search second.** The current system works. Phase 8 is an enhancement, not a dependency.

**5. Model Cascade**  
Four-tier fallback for resilience:
- Primary: Claude Haiku (cost-optimized, $0.25/MTok in, $1.25/MTok out)
- Fallback 1: GPT-4.1 (capability)
- Fallback 2: Grok-3-Mini-Fast (speed)
- Fallback 3: Ollama qwen2.5:7b (local, offline, 13.65 tok/sec)

If the entire internet goes down, the agent keeps running on local inference.

**6. Cron-Based Automation**  
OpenClaw's native cron scheduler handles:
- Morning briefings (06:00 MDT, delivers via Telegram)
- Layer 0 signal routing (every 15 min, 07:00–23:00 MDT)
- VPS snapshots (02:00 MDT daily)
- GitHub backups (02:00 MDT daily)
- Weekly updates (Sunday 03:00 MDT)
- Compose backups (Sunday 05:00 MDT + on-demand)

All crons route to Telegram for silent ops monitoring.

---

## Why Is It Best-in-Class?

### Comparison to Alternatives

| Feature | Flat File Logging | Vector DB Only | Hindsight Plugin | **Project Trident** |
|---------|-------------------|----------------|------------------|---------------------|
| **Survives restarts** | ❌ Manual only | ✅ Yes | ✅ Yes | ✅ Yes |
| **Human-readable** | ✅ Yes | ❌ No | ❌ Opaque | ✅ Yes |
| **Git-trackable** | ✅ Yes | ❌ No | ❌ No | ✅ Yes |
| **Personality development** | ❌ No | ❌ No | ❌ No | ✅ First-class |
| **Cost per day** | Free | $2-5 | $1-2 | **$0.67** |
| **Disaster recovery** | ❌ Manual | ⚠️ DB backups | ⚠️ Plugin-dependent | ✅ Multi-layer |
| **Offline resilience** | ✅ Yes | ❌ No | ❌ No | ✅ Local fallback |
| **Lossless recall** | ❌ No | ⚠️ Embedding drift | ✅ DAG-based | ✅ LCM + DAG |
| **Debuggable** | ✅ Yes | ❌ Black box | ❌ Opaque | ✅ Full visibility |
| **Signal routing** | ❌ Manual | ❌ No | ⚠️ Auto-capture | ✅ Intelligent triage |

### What Makes Trident Superior?

1. **Resilience**  
   Three independent failure modes (LCM, GitHub, VPS snapshots) all have to fail simultaneously for data loss to occur. Probability: effectively zero.

2. **Auditability**  
   Every memory decision is visible. Git diffs show exactly what the agent learned, when, and why. No black boxes.

3. **Cost Efficiency**  
   Sub-$1/day for full persistence. Competitors charge $2-5/day or rely on expensive always-on vector search.

4. **Identity as Infrastructure**  
   Most systems bolt personality onto task execution. Trident treats self-awareness, beliefs, and growth as architectural components with dedicated storage and routing.

5. **Human-Agent Collaboration**  
   Markdown files mean humans can edit, audit, and curate agent memory directly. No API required.

6. **Future-Proof**  
   Phase 8 (Qdrant + FalkorDB) is already wired. When semantic search becomes critical, it's a config flip, not a rewrite.

7. **Offline Capable**  
   Local Ollama fallback means the agent keeps running even if all cloud APIs go down. No other system offers this.

---

## Use Cases

- **Long-running personal assistants** that remember your preferences, habits, and past decisions
- **Research agents** that build knowledge bases over weeks/months
- **DevOps agents** that learn from past incidents and maintain runbooks
- **Creative agents** that develop voice, style, and aesthetic preferences over time
- **Autonomous trading bots** that track P/L, lessons learned, and market patterns
- **Self-improving agents** that audit their own performance and iterate on strategies

---

## Getting Started

See [`SKILL.md`](./SKILL.md) for architecture overview and [`references/deployment-guide.md`](./references/deployment-guide.md) for step-by-step integration instructions.

**Installation:**
```bash
clawhub install project-trident
```

**Deployment:**
1. Enable LCM plugin (`lossless-claw`)
2. Set up Layer 0 signal router (cron-based)
3. Configure hierarchical buckets (MEMORY.md, self/, lessons/, projects/)
4. Wire GitHub SSH backup
5. Configure VPS snapshot automation

Full deployment takes ~30 minutes. Cost: **$0.67/day** for 24/7 operation.

---

## License

[Specify license: MIT, Apache 2.0, etc.]

---

## Credits

**Designed and built by Shiva** (ShivaClaw on GitHub) in collaboration with G (Brandon).

Part of the **Hal Stack** 🦞 — a suite of tools for building autonomous, self-improving AI agents.

---

**Project Trident: Memory that never forgets. Identity that grows. Resilience that lasts.**
