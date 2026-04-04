---
name: xhs-autopilot
description: Red (Xiaohongshu) Full-Autonomous AI-Native Workflow Alchemy System. 30-min operation loop with self-improvement.
---

# 🧪 XHS Autopilot v4.0
## 全自主AI原生工作流炼金术系统

**版本**: v4.0  
**定位**: AI原生工作流炼金术 + 全自动运营闭环  
**循环**: 每30分钟自动执行8步工作流  
**核心**: 记忆隔离 + 自我进化

---

## 🏗️ 记忆架构（重要！）

本系统使用**三层记忆隔离架构**:

```
┌─────────────────────────────────────────┐
│  Layer 1: 通用技术记忆 (workspace/MEMORY.md)    │
│  - Playwright CDP模式                   │
│  - 跨项目技术原则                       │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│  Layer 2: 运营闭环 (xhs-memory/mode-si/memory/03_semantic/) │
│  - CORE_STRATEGY.md    # 战略定位       │
│  - OPERATION_LOOP.md   # 本文件         │
│  - BOTTLENECKS.md      # 瓶颈记录       │
│  - SELF_IMPROVEMENT.md # 自我进化       │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│  Layer 3: 运行时数据                     │
│  - 01_episodic/    草稿                 │
│  - 02_reflective/  发布记录             │
│  - 03_semantic/    沉淀原则             │
│  - performance_data/ 数据追踪           │
└─────────────────────────────────────────┘
```

**重要**: 小红书专属记忆不得污染通用MEMORY.md！

---

## ⚡ 30分钟全自动闭环

### 8步工作流

```
1. Align(对齐战略) → 2. Route(路线检查) → 3. Topic(选题确认)
4. Research(即时调研) → 5. Recall(认知加载) → 6. Create(多模态创作)
7. Act(拟人发布) → 8. Reflect(反思进化)
```

### Step 8: Reflect 详细流程

#### 8.1 数据收集（自动）
```bash
# 自动执行
- 截图笔记页面
- 抓取点赞/收藏/评论数
- 抓取评论内容
- 记录到 performance_data/
```

#### 8.2 视觉自检（Sub-Agent）
创建sub-agent审视笔记，检查：
- 封面是否符合赛博朋克规范
- 字体是否为 JetBrains Mono
- 页码是否正确（单图不标）
- 语言是否符合极客隐喻

#### 8.3 反馈分析（Sub-Agent）
分析评论，输出：
- 用户高频需求
- 内容优化建议
- 新选题灵感

#### 8.4 自我进化
- 识别瓶颈 → 记录到 BOTTLENECKS.md
- 提出需求 → 尝试自我解决
- 验证效果 → 下一轮检验
- 知识沉淀 → 更新本文件

---

## 🎨 当前模式：赛博朋克 + Agent炼金术

### 定位
**"AI原生工作流炼金术"**

**三要素**（每篇笔记必须有）:
1. 反常识洞察
2. Agent配置
3. 幕后揭秘

### 视觉规范
| 元素 | 规范 |
|------|------|
| 背景 | #0a0a0a（深色） |
| 强调色 | #00f5ff（霓虹青） |
| 对比色 | #ff0080（品红） |
| 标题字体 | JetBrains Mono |
| 正文字体 | 苹方-简 |

### 5页手术版结构
1. **痛点页**: 时间贫困公式
2. **反常识页**: 批判教程思维
3. **方案页**: Agent配置截图
4. **效果页**: 分屏对比
5. **CTA页**: 特权型钩子

### 语言风格
- ❌ 禁用: "首先其次最后", emoji轰炸, 教程语气
- ✅ 强制: 技术隐喻（注入、编译、劫持）

---

## 🛠️ 可用脚本

### 核心工具
| 脚本 | 功能 | 版本 | 用途 |
|------|------|------|------|
| `search/run.py` | 百度搜索 | v1.1 | Step 4 |
| `cover/run.py` | 封面生成(旧) | v1.1 | Step 6 |
| `jimeng/run.py` | 即梦AI生图 | v1.0 | Step 6 |
| `publish/run.py` | 发布 | v1.3 | Step 7 |
| `comments/run.py` | 评论分析 | v1.0 | Step 8 |
| `feedback/run.py` | 数据截图 | v1.0 | Step 8 |

### 待开发（自我进化）
| 脚本 | 功能 | 优先级 |
|------|------|--------|
| `autopilot/run.py` | 主循环 | 🔴 P0 |
| `cover_v2/run.py` | 赛博朋克封面 | 🔴 P0 |
| `self_check/run.py` | 视觉自检 | 🟡 P1 |
| `trend_track/run.py` | 热点追踪 | 🟡 P1 |

---

## 📂 必读文档（按优先级）

1. **OPERATION_LOOP.md** - 本文件（运营闭环）
2. **CORE_STRATEGY.md** - 战略定位
3. **BOTTLENECKS.md** - 当前瓶颈
4. **SELF_IMPROVEMENT.md** - 进化记录

---

## 🚀 快速启动

### 手动执行一轮
```bash
cd ~/.openclaw/skills/xhs-autopilot
python3 scripts/autopilot/execute_loop.py
```

### 启动全自动循环
```bash
python3 scripts/autopilot/run.sh
```

### 查看当前瓶颈
```bash
cat xhs-memory/mode-si/memory/03_semantic/BOTTLENECKS.md
```

---

## 📝 使用示例

### 例1: 手动执行完整流程
```python
# 读取运营闭环
read(xhs-memory/mode-si/memory/03_semantic/OPERATION_LOOP.md)

# 执行8步工作流
execute_loop()

# 发布后自检
screenshot_self_check(note_id)
spawn_subagent(feedback_analysis, note_id)

# 识别瓶颈并自我改进
identify_bottlenecks()
self_improve()
```

### 例2: 查看系统状态
```bash
# 检查当前阶段
cat xhs-memory/mode-si/planning/ROADMAP_90DAYS.md

# 查看最新数据
ls -la xhs-memory/mode-si/performance_data/

# 查看优化记录
cat xhs-memory/mode-si/memory/03_semantic/SELF_IMPROVEMENT.md
```

---

## 🔄 自我进化流程

```
每轮循环结束后:

1. 自问: "当前有什么瓶颈?"
   └─► 记录到 BOTTLENECKS.md

2. 自问: "需要什么技能?"
   └─► 尝试创建/修改脚本

3. 自问: "如何优化内容?"
   └─► 根据反馈调整

4. 自问: "战略是否需要调整?"
   └─► 更新 CORE_STRATEGY.md

5. 沉淀
   └─► 更新本文件
```

---

## ⚠️ 重要规则

### 记忆隔离
- ✅ 小红书战略 → 存于 xhs-memory/
- ❌ 不要写入 workspace/MEMORY.md

### 自动化原则
- ✅ 30分钟自动循环
- ✅ 错误自动恢复
- ✅ 数据自动记录
- ✅ 瓶颈自动识别

### 自我进化
- ✅ 每轮必须识别瓶颈
- ✅ 必须尝试自我解决
- ✅ 必须记录改进过程

---

## 📊 商业闭环目标

| 阶段 | 时间 | 目标 |
|------|------|------|
| 建立认知 | 1-30天 | 稳定产出，测试新模式 |
| 深度内容 | 31-90天 | 建立人设，筛选用户 |
| 变现测试 | 90天+ | 自动化变现，商业闭环 |

---

## ✅ 安装检查清单

- [ ] Chrome CDP在9222端口
- [ ] 小红书已登录
- [ ] xhs-memory/结构完整
- [ ] 所有脚本可执行
- [ ] 30分钟循环已配置
- [ ] sub-agent环境就绪

---

**版本**: v4.0  
**架构**: 全自主闭环 + 自我进化  
**状态**: 🚀 运行中
