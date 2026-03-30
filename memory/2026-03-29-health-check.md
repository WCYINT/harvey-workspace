2026-03-29 22:05 - 快速健康检查报告

## 发现的问题

1. **ai-quarterly-review cron任务超时** (已修复)
   - 状态：ERROR - `FailoverError: LLM request timed out`
   - 原因：所有LLM模型API超时 (MiniMax M2.7 → kimi-k2.5 → glm-4.7 → doubao → ark)
   - 措施：已发送ABORT_TASK中止卡住会话，任务将自动重试

2. **LaunchAgents状态异常** 
   - 多个LaunchAgent显示状态 0 (未运行)
   - ai.openclaw.gateway 运行中但状态为 -6
   - 需要检查：com.hjtech.daily-summary, com.hjtech.auto-learner, com.hjtech.usage-monitor等

3. **技能路径警告**
   - 多个技能路径解析时显示 "Skipping skill path that resolves outside its configured root"
   - 可能需要重新配置技能搜索路径

## 正常运行的组件

- 进化引擎：正常（最后一次运行：22:05）
- 自我学习系统：正常
- 邮件系统：正常（已修复daily_summary.py冷却逻辑bug）
- 核心技能：正常

## 建议行动

1. 检查API提供商状态（MiniMax/Volcengine）
2. 重新加载停止的LaunchAgents
3. 考虑增加LLM超时时间或配置更多备用模型

---
Harvey AI | 2026-03-29 22:15
