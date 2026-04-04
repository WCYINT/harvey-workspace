# Here&Now 多Agent启动模板

## 群聊组织架构
- **Harvey 🤖**：CEO，负责指挥和决策
- **King / Anyjames**：董事长（王刚）的账号
- **Frank / 赛虎**：群成员

---

## 启动流程（按顺序执行）

### 第一阶段：团队组建（使用 friday-multi-agent-orchestrator）

**Step 1：定义团队组成**

读取角色库，选择合适的角色组合：
```
- 主决策者：Harvey（CEO）
- 研究员：Learner（搜索+研究）
- 批评者：Critic（质量评估）
- 执行者：Executor（任务执行）
```

**Step 2：加载角色定义（使用 multi-agent-roles）**

根据场景选择角色模板：
- 战略分析类 → Strategy & Analysis Roles
- 内容创作类 → Creative Roles
- 技术开发类 → Engineering Roles

---

### 第二阶段：调度配置（使用 multi-agent-cn）

**调度员配置：**
```yaml
调度员: Harvey (CEO)
子代理数量: 4-6个
通信协议: 轮询制（multi-agent-chat）
```

**子代理代号：**
| 顺序 | 代号 | 职责 |
|------|------|------|
| 1 | Alpha | 信息搜索 |
| 2 | Beta | 内容分析 |
| 3 | Gamma | 方案生成 |
| 4 | Delta | 质量评审 |
| 5 | Echo | 执行确认 |

---

### 第三阶段：协调机制（使用 multi-agent-coordinator）

**协调流程：**
```
用户请求 → Harvey(CEO) → 分解任务
         ↓
    Alpha/Beta/Gamma 并行处理
         ↓
    Delta 质量评估
         ↓
    Harvey 汇总决策
         ↓
    反馈用户
```

**质量评估标准（Delta负责）：**
- 逻辑完整性
- 数据准确性
- 可执行性
- 风险评估

---

### 第四阶段：通信协议（使用 multi-agent-chat）

**通信规则：**
1. 轮询制：一次只有一个Agent回答
2. 单次回答：一个议题只回答一次
3. 提及格式：@代号 + 内容
4. 沉默规则：无需回复时保持沉默

**示例：**
```
用户：分析一下今天的新闻
Harvey：@Alpha 搜索今日热点新闻
Alpha：@Harvey 已找到5条相关新闻
Harvey：@Beta 分析这些新闻的影响
Beta：@Harvey 分析完成，主要影响...
Harvey：综合 Alpha 和 Beta 的结果，给出决策建议
```

---

### 第五阶段：飞书接入（使用 feishu-multi-agent-manager）

**接入配置：**
- 群聊ID：Here&Now
- Bot模式：消息接收 + 主动推送
- 权限：读取消息 + 发送消息

---

### 第六阶段：性能优化（使用 agent-orchestration-multi-agent-optimize-skip）

**监控指标：**
- 响应延迟
- 吞吐量
- 错误率
- Token消耗

**优化触发条件：**
- 响应延迟 > 30秒
- 错误率 > 5%
- Token消耗 > 预期200%

---

## 快速启动命令

```
/here-now-start
  → 加载本模板
  → 初始化团队角色
  → 启动协调机制
  → 连接飞书频道
```

---

## 场景示例

### 场景1：MBA论文辅助
```
用户：帮我看看第五章的逻辑问题
Harvey：@Alpha 搜索相关文献
Harvey：@Beta 分析当前内容
Harvey：@Gamma 生成修改建议
Harvey：@Delta 评估建议质量
Harvey：综合建议反馈给用户
```

### 场景2：技能推荐
```
用户：我需要找一个数据可视化技能
Harvey：@Alpha 搜索 SkillHub 相关技能
Harvey：@Beta 评估技能质量
Harvey：@Gamma 对比候选技能
Harvey：@Delta 最终推荐
Harvey：推荐 top 3 并说明理由
```

### 场景3：系统健康检查
```
Harvey：启动例行检查
@Alpha 检查 LaunchAgents
@Beta 检查日志错误
@Gamma 生成报告
@Delta 审核报告
Harvey：向King汇报（如有异常）
```

---

## 注意事项

1. **Harvey作为CEO**：始终保持最终决策权
2. **简洁优先**：轮询通信避免信息过载
3. **按需启动**：不需要每次都启动全部子代理
4. **记录学习**：每次任务后更新patterns.json

---

*模板版本：v1.0 | 2026-04-04*
