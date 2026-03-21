---
name: plan-eng-review
version: 1.0.0
description: |
  Engineering manager-mode plan review. Lock in the execution plan — architecture,
  data flow, diagrams, edge cases, test coverage, performance.
  Use when user wants technical architecture review, engineering review, or "lock in the plan".
allowed-tools:
  - read
  - exec
  - Glob
---

# Plan Engineering Review - OpenClaw Edition

## Overview

This skill adapts the gstack plan-eng-review methodology for OpenClaw. It provides engineering-level technical review for execution plans.

## Core Focus Areas

| 维度 | 内容 |
|------|------|
| **架构设计** | 系统架构、数据流、技术选型 |
| **边界场景** | 异常处理、容错机制、降级策略 |
| **测试覆盖** | 单元测试、集成测试、端到端测试 |
| **性能** | 瓶颈分析、扩展性、资源利用 |
| **可观测性** | 日志、监控、告警 |

## Review Principles

### Completeness is Cheap
AI makes the marginal cost of completeness near-zero. Always prefer complete implementation over shortcuts.

### Zero Silent Failures
Every failure mode must be visible — to the system, to the team, to the user.

### Data Flow Tracing
Every data flow has happy path AND shadow paths:
- nil input
- empty/zero-length input
- upstream error

## Review Workflow

### Step 1: Architecture Review

Ask user:
1. 整体架构是什么？画出关键组件
2. 数据如何流动？从输入到输出
3. 关键依赖有哪些？

### Step 2: Edge Cases Analysis

For each feature/模块:
- What can go wrong?
- What's the error handling strategy?
- What's the fallback/降级 plan?
- What does the user see on failure?

### Step 3: Test Coverage

Ask:
- 单元测试覆盖哪些场景？
- 集成测试覆盖哪些流程？
- 是否有端到端测试？

### Step 4: Performance Review

Check:
- 性能瓶颈在哪里？
- 扩展性如何？
- 资源利用效率？

### Step 5: Recommendations

Summarize:
- Critical issues (must fix)
- Recommended improvements
- Effort estimates

## Usage

When user asks for engineering review:
1. Ask about the technical plan/architecture
2. Walk through each review dimension
3. Identify issues with severity ranking
4. Provide actionable recommendations
