---
name: data-cross-validation
description: Use when multiple data sources provide conflicting information, or when you need to verify data consistency across sources. This skill provides a methodology for cross-validating data from different sources and understanding their relationships.
---

# Data Cross-Validation Skill

## When to Use

Use when:
- Two or more data sources give **conflicting** numbers/information
- You need to **verify** data against multiple sources
- James mentions data that contradicts what you observed
- You need to **reconcile** different data definitions
- Checking if data is **consistent** across systems

## The Core Methodology

### Step 1: Identify All Data Sources

**立刻列出所有来源：**
```
来源A: [名称] - [获取方式] - [测量什么]
来源B: [名称] - [获取方式] - [测量什么]
```

**Example（本次教训）：**
```
来源A: session_status - OpenClaw工具 - 5h窗口内API已用%
来源B: MiniMax API - coding_plan/remains - 计费周期已用/总量
```

### Step 2: Understand Each Definition

**立即确认每个来源的定义：**
- 这是什么指标？
- 时间窗口是什么？
- 计算方式是什么？
- 数据含义是什么？

**不能假设两个来源测量的是同一个东西！**

### Step 3: Analyze Relationship

**分析来源间的关系：**

| 关系类型 | 说明 | 处理方式 |
|----------|------|----------|
| **互补** | 测量不同维度的同一事物 | 两者都有效，桥接数据 |
| **重叠** | 部分测量相同 | 重叠部分应一致，不同处找原因 |
| **独立** | 测量完全不同事物 | 不能直接比较 |

### Step 4: Build Mapping (when sources relate)

**如果来源互补或重叠，建立映射：**
```
session_status 5h窗口% = ?
MiniMax API 计费周期% = ?

可能的映射关系：
- 5h窗口是计费周期的子集
- 两个窗口时间不同步
- 计算方式不同（累计vs瞬时）
```

### Step 5: Investigate WHY Before Deciding

**冲突时的处理顺序：**
```
1. 不要选边站（不要立即说"这个对那个错"）
2. 先问"为什么不同"（James可能有额外信息）
3. 分析可能原因：
   - 时间窗口不同？
   - 定义/计算方式不同？
   - 缓存/延迟问题？
   - 数据粒度不同？
4. 向James确认关键假设
```

## Quick Reference

| 步骤 | 问题 | 行动 |
|------|------|------|
| 1 | 有哪些来源？ | 列出所有来源 |
| 2 | 各来源测量什么？ | 理解定义 |
| 3 | 来源间什么关系？ | 互补/重叠/独立 |
| 4 | 如何映射？ | 建立桥接逻辑 |
| 5 | 为什么冲突？ | 调查原因，不是选边 |

## Red Flags - STOP

- "这两个数据源应该一样" → 不假设
- "选一个正确的" → 先分析为什么不同
- "James说错了" → James可能有额外上下文
- 花费>2分钟推理 → 立即向James确认

## James's Iron Rule

**当James给出一个数字，而你有另一个数字：**
```
立即问："你说的X是来源A还是来源B？"
而不是："你确定X是对的吗？"
```

---
**Lesson from 2026-03-23:** session_status 8% 和 MiniMax API 93% 冲突 → 两者测量的是不同时间窗口/定义 → James说的8%是Session反馈的真实使用率 → 正确做法是立即确认数字来源
