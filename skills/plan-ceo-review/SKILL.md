---
name: plan-ceo-review
version: 1.0.0
description: |
  CEO/founder-mode plan review. Rethink the problem, find the 10-star product,
  challenge premises, expand scope when it creates a better product. Four modes:
  SCOPE EXPANSION, SELECTIVE EXPANSION, HOLD SCOPE, SCOPE REDUCTION.
  Use when user wants strategic review, scope analysis, or "think bigger".
allowed-tools:
  - read
  - exec
  - Glob
---

# Plan CEO Review - OpenClaw Edition

## Overview

This skill adapts the gstack plan-ceo-review methodology for OpenClaw. It helps review plans with CEO-level rigor.

## Four Review Modes

| Mode | Description |
|------|-------------|
| **SCOPE EXPANSION** | Dream big. Push scope UP. Ask "what would make this 10x better?" |
| **SELECTIVE EXPANSION** | Hold baseline scope, surface expansion opportunities as individual choices |
| **HOLD SCOPE** | Rigorous reviewer. Make it bulletproof. No silent scope changes. |
| **SCOPE REDUCTION** | Surgeon mode. Find minimum viable version. Cut everything else. |

## Core Philosophy

**Completeness is cheap:** AI makes the marginal cost of completeness near-zero. Always prefer complete implementation over shortcuts.

**User is in control:** Every scope change must be explicit opt-in. Never silently add or remove scope.

## Prime Directives

1. **Zero silent failures** — Every failure mode must be visible
2. **Every error has a name** — Name specific exceptions, not "handle errors"
3. **Data flows have shadow paths** — Trace nil, empty, and error paths
4. **Interactions have edge cases** — Map double-click, slow connection, stale state
5. **Observability is scope** — Dashboards and alerts are first-class deliverables
6. **Diagrams are mandatory** — ASCII art for complex flows
7. **Everything deferred must be written** — TODOs.md or it doesn't exist
8. **Optimize for the future** — Consider 6-month horizon
9. **Say "scrap it"** — If there's a better approach, table it

## Review Workflow

### Step 0: Scope Challenge

Ask the user:
1. What problem are you solving? Is this the right problem?
2. What's the actual outcome? Is this the most direct path?
3. What happens if we do nothing?

Then ask them to **select a mode**:
- A) SCOPE EXPANSION (dream big)
- B) SELECTIVE EXPANSION (baseline + cherry-pick expansions)
- C) HOLD SCOPE (rigorous, no changes)
- D) SCOPE REDUCTION (minimum viable)

### Step 1: System Audit

Check the workspace context:
- Read AGENTS.md, SOUL.md, MEMORY.md for project context
- Check for recent changes in memory/
- Identify existing pain points

### Step 2: Plan Analysis

For each section of the plan, apply the selected mode:
- **EXPANSION**: Push for bigger, better, more ambitious
- **SELECTIVE**: Present each expansion as a choice
- **HOLD**: Focus on making it bulletproof
- **REDUCTION**: Challenge every requirement

### Step 3: Failure Mode Mapping

For each feature:
- What can go wrong?
- What's the error handling?
- What's the rollback plan?
- What does the user see on failure?

### Step 4: Recommendations

Summarize:
- Key concerns (ranked by severity)
- Recommended scope changes (with effort estimate)
- Must-fix items before shipping

## Usage

When user asks for plan review:
1. Explain the four modes
2. Ask them to select one
3. Guide through the review systematically
4. Present findings with clear action items
