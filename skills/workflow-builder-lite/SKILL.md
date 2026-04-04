---
name: workflow-builder-lite
description: "Build and simulate multi-step workflows with conditional logic. Chain API calls and agent actions into sequences with if/else branching. Workflows exist only in the current session. Exec steps are simulation-only (the agent describes what would happen without running shell commands). API responses and results are returned in-chat only — never written to files unless the user explicitly requests it separately. Use when: user wants to plan a multi-step process, visualize a pipeline, prototype an automation flow, or think through conditional logic. Homepage: https://clawhub.ai/skills/workflow-builder-lite"
---

# Workflow Builder Lite

**Install:** `clawhub install workflow-builder-lite`

Plan and visualize multi-step workflows with conditional logic. No code required.

**Workflows are session-only — they are never written to files or persisted.** This skill plans and simulates workflows. Execution uses only the agent's built-in tools (message, browser, web_fetch) — no shell exec, no file writes, no external dependencies.

## Language

Detect from the user's message language. Default: English.

## How It Works

### Method 1: Natural Language

> User: "Lag en workflow: hent vær fra wttr.in → hvis regn → send meg melding"
>
> Agent: Her er foreslått workflow:
> ```
> 1. ⛅ Hent vær (GET wttr.in/Oslo?format=j1)
> 2. 🔀 Sjekk: Er det regn? (vurder weather_description)
>    → Ja: 3. 📨 Send melding "Ta paraply!" til bruker
>    → Nei: Stop (ingen handling)
> ```
> Godkjent? (ja/nei/rediger)

### Method 2: Step-by-Step

> "Legg til et steg: hent data fra API X"
> "Legg til betingelse: hvis status != 200, stopp"
> "Legg til et steg: lagre resultat som variabel for neste steg"

### Method 3: Edit Existing

> "Vis workflow 'morning brief'"
> "Endre steg 2 til å bruke endpoint Y i stedet"
> "Legg til et nytt steg etter steg 3"

## Running a Workflow

### Execution

When the user approves a workflow, the agent executes it step by step using built-in tools:

- **API steps**: Use the agent's built-in HTTP capabilities (or suggest smart-api-connector for complex REST calls). Results are returned in-chat only.
- **Agent steps**: The agent uses only built-in tools (message, browser, web_fetch). No file writes, no shell commands.
- **Exec steps**: NOT supported — this skill does not run shell commands. If a step requires shell access, suggest the user set up a cron job or run the command manually.

### Progress Reporting

```markdown
## ⚙️ Kjører: Morning Brief

| # | Steg | Status | Resultat |
|---|------|--------|----------|
| 1 | Hent vær | ✅ | 12°C, delvis skyet |
| 2 | Sjekk regn | ⏭️ | Ingen regn → hopp over steg 3 |
| 3 | Send melding | — | Hoppet over |

**Resultat:** Fullført. 2/3 steg kjørt.
```

### Error Handling

| Step Error | Action |
|-----------|--------|
| Network failure | Retry once, then ask user |
| API returns 4xx | Stop workflow, show error |
| API returns 5xx | Retry 2x with delay, then stop |
| Invalid data | Skip step, log warning, continue |
| Condition parse error | Ask user to clarify |

### Dry Run / Simulation

User says: "dry run workflow X" / "test X"

- Walk through all steps WITHOUT executing anything
- Show what WOULD happen at each step
- Highlight potential issues
- No side effects whatsoever

## Workflow Commands

| User says | Action |
|-----------|--------|
| "create workflow" / "lag workflow" | Start workflow builder |
| "show workflows" / "vis workflows" | List workflows in this session |
| "run X" / "kjør X" | Execute workflow |
| "dry run X" / "test X" | Simulate without executing |
| "edit workflow X" | Modify existing workflow |

## Limitations

- Workflows exist in session context only — closing the session loses them
- Maximum 5 steps per workflow
- Simple if/else branching (no nesting)
- No shell/exec steps — use cron or manual commands for those
- No file persistence — workflow definitions and results exist only in chat
- No cron scheduling (use the agent's built-in cron tool directly if needed)
- **Explicit file I/O is out of scope** — if the user wants to save API results to a file, recommend they use the `exec` tool separately after the workflow completes

## Output Format

Adapts to user language.

### English / Norwegian

```markdown
## ⚙️ Workflow: {name}

**Status:** Running / Completed / Failed
**Steps:** X/Y completed | **Time:** {X}s

| # | Step | Status | Result |
|---|------|--------|--------|
```

## More by TommoT2

- **smart-api-connector** — Connect to any REST API without writing code
- **setup-doctor** — Diagnose and fix OpenClaw setup issues
- **tommo-skill-guard** — Security scanner for all installed skills
