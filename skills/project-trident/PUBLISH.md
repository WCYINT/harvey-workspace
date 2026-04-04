# Trident Memory — ClawHub Publication

## Pre-Publication Checklist

- [x] SKILL.md complete with frontmatter + markdown body
- [x] references/deployment-guide.md (step-by-step integration)
- [x] references/cost-tuning.md (budget profiles)
- [x] scripts/layer0-agent-prompt-template.md (base prompt template)
- [x] Pushed to GitHub (ShivaClaw/shiva-memory)
- [x] .gitignore configured (allowlist-only, no private data)
- [x] No SOUL.md, USER.md, MEMORY.md, or personal data included ✓

## Publication Steps

### 1. Authenticate with ClawHub

```bash
clawhub login
# Follow browser/token flow
clawhub whoami  # Verify logged in
```

### 2. Publish Trident

```bash
clawhub publish /data/.openclaw/workspace/trident-skill \
  --slug "trident-memory" \
  --name "Trident Memory" \
  --version "1.0.0" \
  --changelog "Initial release: Three-tier persistent memory architecture for OpenClaw agents. Features: LCM-backed durability (Phase 1), hierarchical .md buckets (Phase 2), agentic signal routing (Phase 5, Layer 0), encrypted GitHub+VPS backups (Phase 7). Solves blank-spots problem and supports autonomous agent growth."
```

### 3. Verify Publication

```bash
clawhub search "trident-memory"
clawhub info trident-memory  # View published skill
```

### 4. Installation Test (Optional)

In a test environment:

```bash
clawhub install trident-memory
```

Then follow `references/deployment-guide.md` to integrate.

## Metadata

- **Name:** Trident Memory
- **Slug:** trident-memory
- **Version:** 1.0.0
- **Registry:** https://clawhub.com (default)
- **Description:** Three-tier persistent memory architecture for OpenClaw agents
- **Tags:** memory, persistence, agent-continuity, backup, signal-routing
- **Author:** Shiva (ShivaClaw on GitHub)
- **License:** [Choose: MIT, Apache 2.0, etc. — add to SKILL.md frontmatter if desired]

## Future Updates

When publishing new versions:

```bash
# Increment version in command below
clawhub publish /data/.openclaw/workspace/trident-skill \
  --slug "trident-memory" \
  --version "1.1.0" \
  --changelog "Phase 8 integration guide added; Qdrant+FalkorDB deployment steps"
```

---

**Ready to publish? Run:**

```bash
clawhub login && clawhub publish /data/.openclaw/workspace/trident-skill \
  --slug "trident-memory" \
  --name "Trident Memory" \
  --version "1.0.0" \
  --changelog "Initial release: Three-tier persistent memory architecture for OpenClaw agents. Features: LCM-backed durability, hierarchical buckets, agentic signal routing, encrypted backups."
```
