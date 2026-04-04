# Here&Now 多Agent启动模板

## 简介

这是 Here&Now 群聊的多Agent管理体系的核心启动模板，整合了7个多Agent技能形成完整协作体系。

## 功能

1. **团队组建** - 使用 friday-multi-agent-orchestrator 定义团队组成
2. **角色配置** - 使用 multi-agent-roles 选择专业角色模板
3. **任务调度** - 使用 multi-agent-cn 进行指挥官调度
4. **质量协调** - 使用 multi-agent-coordinator 协调子代理
5. **通信协议** - 使用 multi-agent-chat 轮询通信
6. **飞书接入** - 使用 feishu-multi-agent-manager 接入群聊
7. **性能优化** - 使用 agent-orchestration-optimize-skip 监控优化

## 群聊组织架构

- **Harvey 🤖**：CEO，负责指挥和决策
- **King / Anyjames**：董事长（王刚）的账号
- **Frank / 赛虎**：群成员

## 使用方法

启动流程：
```
/here-now-start
  → 加载模板
  → 初始化团队角色
  → 启动协调机制
  → 连接飞书频道
```

## 相关技能

- multi-agent-cn
- multi-agent-roles
- multi-agent-coordinator
- multi-agent-chat
- friday-multi-agent-orchestrator
- agent-orchestration-multi-agent-optimize-skip
- feishu-multi-agent-manager

## 版本

v1.0 | 2026-04-04
