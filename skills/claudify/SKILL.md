---
name: agentify
depends-on: [skill-toolkit]
description: Convert functionality into Claude Code automation. Use when the user says "agentify", "agentic", "automate this", "create an agent", "make a plugin", "make a skill", or wants to automate a workflow as an agent, skill, or plugin.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Skill
  - Bash(mkdir:*)
---

# Agentify

Guide users to convert functionality into the appropriate Claude Code automation type.

## When to Use

- User says "agentify [something]" or just "agentify"
- User wants to create an agent, skill, or plugin
- User wants to automate a repetitive workflow

## Quick Reference

| Type | Trigger | Best For |
| ---- | ------- | -------- |
| **Skill** | Auto (context match) | Instructions, domain guidance |
| **Agent** | Task tool delegation | Multi-step execution, tools |
| **Rules** | Auto (session start) | AI behavior constraints, project conventions |
| **Slash Command** | User types `/cmd` | Simple prompt templates |
| **Hook** | Events (tool use, etc) | Automation on actions |

→ Full comparison: [automation-decision-guide.md](./resources/automation-decision-guide.md)

## Workflow

### Step 1: Analyze Target & Check Duplicates

**If no target specified** ("agentify" alone):
- Review conversation for automation candidates
- Look for: verbose outputs, multi-step workflows, repeated patterns
- ⚠️ **MUST use `multiSelect: true`** when presenting candidates (users often want multiple)

**If target specified**:
1. Check local marketplaces first:
   - `~/.claude/plugins/marketplaces/*/plugins/*/`
   - Use `/skill-dedup` command to find overlaps
2. If not found locally, search remote: `WebFetch https://claudemarketplaces.com/?search=[keyword]`
3. If found → recommend existing or extend. If not → proceed to create

### Step 1.5: Merge 분석 (⚠️ 복수 선택 시 필수)

복수 후보가 선택되면 **반드시** 그룹핑 후 AskUserQuestion으로 merge 여부를 먼저 확인한다.

**그룹핑 기준:**
- 같은 도메인/서비스 (예: 모두 "openclaw" 관련)
- 같은 컨텍스트에서 호출됨
- 하나의 단어로 묶을 수 있음 (예: "openclaw 관리")

**merge 판단 기준:**

| 조건 | 권장 |
|------|------|
| 같은 도메인, 3개 이하 기능 | **multi-topic Skill** |
| 각각 독립 트리거 + 긴 실행 흐름 | 별도 Agent |
| 지시사항 위주 + 일부 Bash | **Skill** (Agent 아님) |
| 복잡한 multi-step + 여러 tool | Agent |

**AskUserQuestion 예시 (merge 여부):**
```
"모두 'openclaw' 도메인입니다. 어떻게 구성할까요?"
options:
  - "하나의 다중 토픽 스킬로 합치기 (openclaw 스킬 → exec/gateway/test 토픽)"
  - "각각 별도 에이전트로 생성"
  - "스킬 + 에이전트 혼합 (지시사항=스킬, 실행=에이전트)"
```

**⚠️ 금지**: merge 여부 확인 없이 관련 기능을 무조건 별도 에이전트로 생성하지 말 것.

### Step 2: Gather Requirements

Use AskUserQuestion to clarify:
- **Trigger**: Automatic / Manual / Event-based
- **Scope**: Global (`~/.claude/`) / Project (`.claude/`)
- **Language**: code comments, variable names, documentation

→ Question patterns: [askuserquestion-patterns.md](./resources/askuserquestion-patterns.md)

### Step 3: Recommend Type

| Requirements | Type |
| ------------ | ---- |
| Auto + instructions | Skill |
| Auto + tool execution | Agent |
| Auto + constraints/conventions | Rules |
| Manual + simple | Slash Command |
| Event reaction | Hook |

### Step 4: Create

⚠️ **CRITICAL**: Follow the creation method for each type

**Skill with scripts** → 스크립트가 있으면 반드시 skill 디렉토리 구조로 생성:
```
skill-name/
├── SKILL.md          ← frontmatter + 사용법 + node scripts/xxx.js 실행 지침
├── topic-a.md        ← 알파벳순
├── topic-b.md        ← 알파벳순
└── scripts/
    └── xxx.js        ← 실제 로직 (tmp 파일 금지, 여기에 영구 보관)
```
- `tmp_*.js` 같은 임시 파일로 만들지 말고 `scripts/` 안에 영구 파일로 생성
- SKILL.md에서 `node <skill-dir>/scripts/xxx.js <mode>` 형태로 실행
- 스크립트 경로는 `__dirname` 기준 상대경로 사용
- **토픽 파일 및 SKILL.md 토픽 테이블은 반드시 알파벳순으로 정렬**

**Skill (no scripts)** → **MUST** use skill-writer (do NOT create directly)
```
Skill tool: skill: "project-automation:skill-writer"
```

**Agent** → Create in `~/.claude/agents/` or `.claude/agents/`
→ [agent-templates.md](./resources/agent-templates.md)

**Rules** → Create in `~/.claude/rules/` or `.claude/rules/`
→ [rules-guide.md](./resources/rules-guide.md)

**Slash Command** → Create in `~/.claude/commands/` or `.claude/commands/`
→ [slash-command-syntax.md](./resources/slash-command-syntax.md)

**Hook** → Add to settings.json
→ [hook-examples.md](./resources/hook-examples.md)

**Plugin** (open source) →
→ [plugin-creation.md](./resources/plugin-creation.md)

### Step 5: Validate

- Verify file location
- Test activation/invocation
- Confirm expected behavior

## Plugin Structure

**Marketplace vs Cache**:
- **Marketplace** (`~/.claude/plugins/marketplaces/<marketplace>/plugins/<plugin>/`): Source of truth, edit here
- **Cache** (`~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/`): Runtime copy, loaded on session start

**Important**: Cache is loaded at session start. Marketplace edits require:
1. Manual sync to cache, OR
2. New session to reload

**Auto-sync hook**: `plugin-cache-sync.sh` syncs marketplace → cache on Edit/Write

## Output Guidelines

Keep responses concise:
- Use tables over verbose lists
- Link to references instead of inline
- Use AskUserQuestion instead of text options

## AskUserQuestion Defaults

| Context | multiSelect |
|---------|-------------|
| Automation candidates | **true** (users often want multiple) |
| **Merge 여부** (복수 선택 후) | **false** (merge vs 분리 - 상호 배타적) |
| Type selection | false (mutually exclusive) |
| Scope selection | false (one location) |
| Feature selection | **true** (additive choices) |

## 실패 사례

**❌ 잘못된 흐름 (2026-03-09)**:
- openclaw 관련 3가지 기능 선택됨
- merge 여부 확인 없이 바로 별도 에이전트 3개 생성
- 결과: 유사 에이전트 난립, 사용자 불만

**✅ 올바른 흐름**:
1. 3가지 후보 선택됨
2. "모두 openclaw 도메인 - merge할까요?" AskUserQuestion
3. "스킬로 merge" 선택 → skill-writer로 multi-topic 스킬 생성

## Ralph 모드 (AskUserQuestion 불가)

`.ralph/` 디렉토리가 존재하면 Ralph 모드로 동작합니다.

**동작 변경**:

| 단계 | 사용자 세션 | Ralph 모드 |
|------|-----------|-----------|
| Step 1: 대화 스캔 | AskUserQuestion (multiSelect) | 전체 후보를 `.ralph/improvements.md`에 기록 |
| Step 1.5: Merge 분석 | AskUserQuestion | 추천 구성을 improvements.md에 기록 |
| Step 2: 요구사항 수집 | AskUserQuestion | 추천 trigger/scope를 improvements.md에 기록 |
| Step 3: 유형 추천 | 추천 제시 | 추천을 improvements.md에 기록 |
| Step 4: 생성 | 실제 생성 | **금지** — `[NEEDS_REVIEW]` 기록만 |
| Step 5: 검증 | 검증 | **스킵** (생성 안 했으므로) |

**improvements.md 기록 형식**:

```markdown
## Agentify 후보 (날짜)

### [패턴 이름]
- **발견**: [대화에서 어떻게 발견했는지]
- **추천 유형**: [Skill/Agent/Hook/Slash Command]
- **추천 구성**: [단일/multi-topic/merge 등]
- **이유**: [왜 이 유형이 적합한지]
- **태그**: [NEEDS_REVIEW]
```

## 자가개선

이 스킬 호출 완료 후, **대화를 기반으로 자가개선**:

1. 대화에서 이 스킬의 한계·실패·우회 패턴 탐지
2. 개선 후보 발견 시 `/skill-toolkit upgrade agentify` 실행
