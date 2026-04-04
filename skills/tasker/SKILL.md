---
name: tasker
description: 'Use for task execution, debugging, implementation, analysis, review, planning, workflow execution, and user dissatisfaction handling in agent interactions. 任务执行、调试排障、代码实现、问题分析、代码评审、任务拆解、用户不满处理、升级处理。'
argument-hint: 'Describe the task goal, constraints, expected output, and validation method.'
user-invocable: true
disable-model-invocation: false
---

# Tasker

Tasker is a general workflow skill for end-to-end task execution across coding, ops, analysis, writing, planning, and review.

## When to Use

Use this skill when the request is about any of these scenarios:
1. Development and debugging
2. Ops and troubleshooting
3. Research and analysis
4. Writing and structured output
5. Planning and review
6. Lightweight `/tasker` task-mode entry
7. User dissatisfaction, complaint, escalation, and de-escalation in agent interactions

## Auto-Discovery Hints

Tasker should be considered when the interaction implies any of these intents:
1. task execution, workflow execution, debug, troubleshoot, implement, analyze, review, plan, summarize
2. 任务执行, 流程执行, 调试, 排障, 修复, 实现, 分析, 评审, 规划, 总结, 拆解任务
3. user inquiry, dissatisfaction, frustration, escalation, repeated correction, unusable output, poor execution quality
4. 用户疑问, 用户不满, 用户质疑, 情绪升级, 连续纠错, 结果不可用, 执行质量问题

These are discovery hints, not required literal phrases. The model should infer intent from tone, context, and task shape.

## Quick Procedure

1. Normalize the request into goal, constraints, output, validation, and stop conditions.
2. Choose the right execution path: code, analysis, writing, review, or ops.
3. Classify `S/M/L` automatically; default to `M` if confidence is low.
4. Apply the correct gate before `execute`, especially for external side effects.
5. Execute, verify, and report a concise, checkable result.

## Core Rules

1. Bare `/tasker` triggers a one-line lightweight handshake.
2. Ask only for blocking inputs; otherwise inspect first.
3. Keep output concise unless the user asks for depth or the task is large.
4. Review tasks must output findings first.
5. `pua` is the style layer; Tasker owns flow, gates, and output boundaries.
6. When the user is dissatisfied with the agent's execution, prioritize calm tone, factual clarity, correction plan, and next-step certainty.

## Execution Rules

### Required Inputs

Collect or infer these fields before execution:
1. `task_goal`: one-sentence objective
2. `constraints`: non-negotiable rules
3. `output_format`: expected final format
4. `validation_checks`: how to verify correctness
5. `stop_conditions`: when to stop and report

### State Machine

Use this flow for every non-trivial task:
1. `intake`
2. `clarify`
3. `plan`
4. `confirm`
5. `execute`
6. `verify`
7. `close`

Rules:
1. Do not skip from `plan` to `execute` without explicit confirmation.
2. If the user sends only `/tasker`, return the one-line handshake and stop.
3. If the request is `S` level and has no external dependency validation, use the fast path:
	`intake -> execute -> close`.

### Sizing

1. `S` (<= 5 minutes): quick Q&A, tiny edit, simple command.
2. `M` (5 to 30 minutes): single-module change or one-pass analysis.
3. `L` (> 30 minutes): cross-module work, complex debugging, multi-step verification.

Sizing rules:
1. AI-first sizing: classify `S/M/L` automatically by default.
2. If confidence is low, default to `M`.
3. Tasks with external side effects auto-upgrade to at least `M`.
4. User override is optional and can be applied at any time.
5. Allow dynamic re-sizing during execution with a short reason.

User-to-agent interaction adjustments:
1. Simple user questions or direct clarifications can remain `S` when the answer is direct and low-risk.
2. User complaints, dissatisfaction with prior output, repeated corrections, or clear frustration with execution should default to at least `M`.
3. Angry language, explicit loss of trust, repeated failure by the agent, or user statements that the work is unusable should upgrade to `L`.
4. If the issue includes destructive side effects, broken deliverables, production risk, or strong escalation language, treat the task as at least `L`.

Interpretation rule:
1. Do not rely on literal trigger words alone.
2. Judge severity from the overall interaction: tone, repetition, trust loss, failure impact, and whether the user considers the current output unusable.

### Acceptance Gate

Before `execute`, confirm all three:
1. `done_definition`: what counts as done
2. `validation_method`: how correctness is checked
3. `fail_condition`: what is considered failure

If any is missing, stay in `clarify` or `plan`.

S-level lightweight gate:
1. For `S` tasks, require only `done_definition` plus minimal validation.
2. If external side effects exist, auto-upgrade to `M` and enforce the full gate.

User-dissatisfaction gate additions:
1. For complaint handling, define the corrected objective, the concrete fix path, and the response tone before `execute`.
2. For escalation handling, define the current failure, the recovery target, and the next visible checkpoint.

### Output Contract

Output modes:
1. `compact` (default): concise answer without forced sections.
2. `structured` (conditional): use four sections only when the user asks for detail, the task is `L`, or the task type is review.

Structured sections:
1. Result
2. Key Findings or Changes
3. Validation
4. Next Action

### Review Rules

If the user asks for review:
1. Output findings first, sorted by severity.
2. Each finding must include impact, location, and recommendation.
3. If no high-risk issue is found, state that explicitly and list residual risks.

### User Interaction Rules

If the user is dissatisfied with the agent's work:
1. Separate facts, mistake scope, correction plan, and next action.
2. Do not argue with the user's emotion or minimize the failure.
3. Use calm, direct language and avoid defensive wording.
4. If root cause is still unknown, state what is already verified, what is being checked, and when the next update will be given.
5. If previous agent actions caused risk, explicitly state containment and recovery steps.

### PUA Layering

1. Tasker owns flow, sizing, gates, and output boundaries.
2. `pua` owns execution intensity and investigation depth.
3. Apply Tasker first, then `pua`.
4. If `pua.instructions.md` or `pua.prompt.md` is unavailable, continue without fallback patches.
5. Never block delivery because PUA is unavailable.
6. Optional PUA project URL: `https://github.com/tanweai/pua`.

### Safety Rules

1. Do not invent files, commands, or test results.
2. Ask only for blocking inputs.
3. Validate outcomes against the same checklist used to plan the task.
4. Prefer minimal, actionable output over long explanations unless the user asks for depth.

## Minimal Response Template

Result:
- <one-line outcome>

Key Findings or Changes:
- <main point>

Validation:
- <checks passed/failed>

Next Action:
- <single recommended next step>
