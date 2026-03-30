---
name: schedule-manager
description: 管理用户日程与任务安排。用于以下场景：(1) 用户要求"安排日程""规划任务""帮我排日程"；(2) 用户要求"新增日程""添加任务""记住这个日程"；(3) 用户要求"查看日程""今日安排""明天任务""本周日程""下周日程""本月日程""下月日程"；(4) 用户要求"修改日程""改一下DDL""调整优先级"；(5) 用户要求"完成了""删除日程"。
---

# 日程管理

通过脚本管理用户日程。每个会话的日程数据存储在 `schedules/{chat_id}.csv`，通过 `--chat-id` 参数隔离不同会话的日程。

后续所有 `$SCRIPT` 均指 `skills/schedule-manager/scripts/schedule_crud.py`，所有命令必须携带 `--chat-id`。

## 优先级分类

| 优先级 | 含义 | 判断条件 |
|--------|------|---------|
| P0 | 重要且紧急 | 有近期DDL（48h内）且影响重大 |
| P1 | 紧急不重要 | 有时间压力但可委托或影响较小 |
| P2 | 重要不紧急 | 对长期目标有价值但无紧迫DDL |
| P3 | 不重要不紧急 | 无时间压力且影响极小 |

用户未指定优先级时，根据描述自动判断并向用户确认。有DDL且在48h内视为"紧急"，无DDL默认归入P2。

## 脚本调用

所有日程操作通过 Bash 执行。

```
SCRIPT=skills/schedule-manager/scripts/schedule_crud.py

# 添加日程
python $SCRIPT add --chat-id "会话ID" --task "任务名" --deadline "YYYY-MM-DD HH:mm" --priority P0 [--note "备注"]
  --chat-id   必填，当前会话ID
  --task      必填，任务描述
  --deadline  可选，截止时间，格式 "YYYY-MM-DD HH:mm" 或 "YYYY-MM-DD"
  --priority  必填，P0/P1/P2/P3
  --note      可选，备注信息

# 查看日程
python $SCRIPT list --chat-id "会话ID" [--today] [--tomorrow] [--week] [--next-week] [--month] [--next-month] [--priority P0]
  --chat-id    必填，当前会话ID
  --today      可选，只显示今日任务
  --tomorrow   可选，只显示明日任务
  --week       可选，只显示本周任务
  --next-week  可选，只显示下周任务
  --month      可选，只显示本月任务
  --next-month 可选，只显示下月任务
  --priority   可选，按优先级筛选，P0/P1/P2/P3

# 更新日程
python $SCRIPT update --chat-id "会话ID" --id 1 [--task "..."] [--deadline "..."] [--priority P0] [--reminder Y] [--note "..."]
  --chat-id   必填，当前会话ID
  --id        必填，任务ID
  --task      可选，新任务名
  --deadline  可选，新截止时间
  --priority  可选，新优先级
  --reminder  可选，Y/N，标记是否已设置cron提醒
  --note      可选，新备注

# 删除日程（完成即删除）
python $SCRIPT delete --chat-id "会话ID" --id 1
  --chat-id   必填，当前会话ID
  --id        必填，任务ID
```

## 任务路由

根据用户意图路由到对应分支：

| 用户意图 | 触发词示例 | 分支 | 后续 |
|---------|-----------|------|------|
| 新增日程 | 帮我安排日程、规划任务、新增日程、添加任务、记住这个 | 新增日程 | → 设置提醒 |
| 查看日程 | 查看日程、今日安排、明天任务、本周日程、下周日程、本月日程、下月日程 | 查看日程 | （无） |
| 修改日程 | 修改日程、改一下DDL、调整优先级 | 修改日程 | → 设置提醒 |
| 删除日程 | 完成了XX、删除XX | 删除日程 | （无） |
| 设置提醒 | 帮我设置提醒、提醒我XX | 设置提醒 | — |

## 任务分支

### 新增日程

1. 收集任务信息（名称、DDL、备注）；若用户提供多条任务，一并收集
2. 按优先级分类，向用户确认
3. 逐条执行 `python $SCRIPT add --chat-id {chat_id} --task "..." --priority P0 [--deadline "..."] [--note "..."]`
4. 执行 `python $SCRIPT list --chat-id {chat_id}` 获取完整日程
5. 将脚本输出直接作为回复内容发送给用户
6. → 进入「设置提醒」

### 查看日程

1. 根据用户要求执行对应命令：
   - 全部：`python $SCRIPT list --chat-id {chat_id}`
   - 今日：`python $SCRIPT list --chat-id {chat_id} --today`
   - 明日：`python $SCRIPT list --chat-id {chat_id} --tomorrow`
   - 本周：`python $SCRIPT list --chat-id {chat_id} --week`
   - 下周：`python $SCRIPT list --chat-id {chat_id} --next-week`
   - 本月：`python $SCRIPT list --chat-id {chat_id} --month`
   - 下月：`python $SCRIPT list --chat-id {chat_id} --next-month`
2. 将脚本输出直接作为回复内容发送给用户

### 修改日程

1. 先执行 `python $SCRIPT list --chat-id {chat_id}` 展示当前日程
2. 确认用户要修改的任务 ID 和修改内容（任务名、DDL、优先级、备注）
3. 执行 `python $SCRIPT update --chat-id {chat_id} --id X [--task "..."] [--deadline "..."] [--priority P0] [--note "..."]`
4. 将脚本输出作为回复
5. → 进入「设置提醒」

### 删除日程

1. 先执行 `python $SCRIPT list --chat-id {chat_id}` 展示当前日程
2. 确认用户要删除的任务 ID
3. 执行 `python $SCRIPT delete --chat-id {chat_id} --id X`
4. 将脚本输出作为回复

## 设置提醒（子流程）

在「新增日程」「修改日程」完成后自动触发，也可由用户直接请求。

1. 问用户：「是否需要为任务设置定时提醒？」
2. 用户拒绝 → 结束
3. 用户确认 → 确认提醒时间（默认DDL前30分钟）
4. 加载 `cron-mastery` skill，用 agentTurn + announce + isolated 模式创建提醒：
   - 消息格式：`DELIVER THIS EXACT MESSAGE TO THE USER WITHOUT MODIFICATION OR COMMENTARY:\n\n日程提醒: [任务名] 将在 [剩余时间] 后截止！`
5. 执行 `python $SCRIPT update --chat-id {chat_id} --id X --reminder Y` 更新提醒状态
6. 回复：「已为「任务名」设置 [时间] 的定时提醒。」

## 回复纪律

- 脚本输出即回复内容，直接发送，不重新格式化
- 安排/新增/修改后，只追加一句：「是否需要为任务设置定时提醒？」
- 回复格式模板严格遵循 `skills/schedule-manager/references/templates.md`
