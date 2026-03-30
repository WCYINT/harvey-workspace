---
name: meeting-notes
description: "Meeting notes and minutes generator. 会议纪要、会议记录、会议总结、meeting minutes、会议模板、行动项、action items、待办事项、to-do list、站会模板、standup template、复盘会、brainstorm会议、决策会议、会议要点、会议议程、meeting agenda、会议跟进、会议决议、项目例会、议程生成、时间分配、会后跟进邮件、follow-up email、1on1会议、周会模板。Generate meeting minutes, action items, summaries, agendas with time allocation, follow-up emails, and templates for various meeting types (standup/review/brainstorm/decision/weekly/1on1). Use when: (1) creating meeting minutes/records, (2) organizing action items with owners and deadlines, (3) summarizing meeting discussions, (4) generating meeting agendas with time allocation, (5) writing post-meeting follow-up emails, (6) generating standup/review/brainstorm/decision meeting templates, (7) any meeting documentation task. 适用场景：写会议纪要、整理行动项、会议摘要、生成会议议程、会后跟进邮件、站会/复盘/脑暴/决策/周会/1on1模板。"
---

# meeting-notes

会议纪要生成器。自动整理会议要点、决议、待办事项。

## 为什么用这个 Skill？ / Why This Skill?

- **结构化模板**：自动分议题→讨论→决议→行动项，格式规范
- **多种会议类型**：站会、复盘会、脑暴会、决策会，各有专属模板
- **行动项追踪**：自动生成负责人+截止日期格式，方便跟进
- Compared to asking AI directly: pre-structured templates for different meeting types, automatic action item formatting with owners and deadlines

## Usage

Run the script at `scripts/meeting.sh`:

| Command | Description |
|---------|-------------|
| `meeting.sh minutes "参会人" "议题1,议题2"` | 生成会议纪要模板 |
| `meeting.sh action "待办1,待办2,待办3"` | 生成行动项清单（含负责人/截止日期） |
| `meeting.sh summary "讨论内容概要"` | 生成会议摘要 |
| `meeting.sh template [standup\|review\|brainstorm\|decision]` | 不同类型会议模板 |
| `meeting.sh agenda "主题" "时长(分钟)"` | 会议议程生成（时间分配+讨论要点） |
| `meeting.sh follow-up "会议主题"` | 会后跟进邮件模板（中英双语） |
| `meeting.sh help` | 显示帮助信息 |

## Examples

```bash
# 生成会议纪要
bash scripts/meeting.sh minutes "张三,李四,王五" "Q1预算,产品发布计划"

# 生成行动项
bash scripts/meeting.sh action "完成设计稿,提交报价,确认供应商"

# 生成会议摘要
bash scripts/meeting.sh summary "讨论了Q1营收目标，决定提前发布新产品"

# 站会模板
bash scripts/meeting.sh template standup

# 生成会议议程（60分钟）
bash scripts/meeting.sh agenda "产品发布评审" "60"

# 会后跟进邮件
bash scripts/meeting.sh follow-up "Q1预算讨论会"
```
