# Team Memory - OpenCode 团队记忆管理

> **给团队每个人建立上下文，用时间轴记录成长轨迹**

## 🌟 核心特点

1. **时间轴格式**: 按时间顺序记录，像日记一样自然可读
2. **纯 Markdown**: 开源可迁移，任何工具都能打开，终身可用
3. **个人独立文件**: 每个成员一个时间轴，方便管理和查看
4. **AI 辅助**: OpenCode 帮你记录、整理、生成报告

## 📁 文件结构

```
team-memory/
├── SKILL.md                      # Skill 定义（精简版）
├── skill-config.yaml             # 团队配置
├── references/                   # 参考文档
│   ├── 场景示例.md              # 完整输出示例
│   ├── 记录模板.md              # 模板详情
│   └── 故障排除.md              # 疑难解答
├── scripts/                     # 脚本工具
│   ├── init.sh                  # 初始化脚本
│   └── new-member.sh            # 创建新成员
└── data/                        # 数据目录
    ├── members/                 # 成员时间轴
    ├── manager-journal/          # 管理反思
    │   └── tracker/            # 自动追踪
    └── insights/                 # 洞察分析
```

## 🚀 快速开始（5分钟）

### 第一步：安装目录（1分钟）

在 PowerShell 或终端中执行：

```powershell
# 创建目录结构
$SkillDir = "$env:USERPROFILE\.config\opencode\skills\team-memory"
$DataDir = "$SkillDir\data"
New-Item -ItemType Directory -Force -Path "$DataDir\members"
New-Item -ItemType Directory -Force -Path "$DataDir\insights"
New-Item -ItemType Directory -Force -Path "$DataDir\templates"
New-Item -ItemType Directory -Force -Path "$DataDir\archive"

# 复制配置文件
Copy-Item "C:\Users\$env:USERNAME\Desktop\SKILL.md" "$SkillDir\SKILL.md"
Copy-Item "C:\Users\$env:USERNAME\Desktop\skill-config.yaml" "$SkillDir\skill-config.yaml"

Write-Host "✅ Team Memory Skill 安装完成！" -ForegroundColor Green
```

### 第二步：配置你的团队（2分钟）

编辑 `~/.config/opencode/skills/team-memory/skill-config.yaml`：

1. **修改成员列表**：将示例的9人替换为你的真实团队成员
2. **保持编号**：使用 member-001 到 member-009
3. **设置别名**：方便快速输入（如 ZS、LS）

### 第三步：创建个人时间轴（重要）

1. 复制模板文件：
```powershell
copy "模板-成员时间轴.md" "张三-时间轴.md"
```

2. 编辑 `张三-时间轴.md`，填写基本信息

3. **开始使用时间轴记录**！

#### 场景1：记录观察（两种方式）

**方式A: 直接编辑文件**（推荐，快速直观）

打开 `张三-时间轴.md`，在顶部添加：
```markdown
### 2024-01-26（周五）
#### 15:30 - 代码Review
**事件**: 张三Review了我的PR，提出了很好的优化建议  
**类别**: 协作沟通  
**评价**: ⭐⭐⭐⭐ 良好  
**标签**: #代码质量 #技术深度

**观察笔记**:  
- 对代码质量要求高
- 表达方式友好，建议有建设性

**后续行动**:  
- [x] 已按建议修改
```

**方式B: 通过 OpenCode**（方便，自然语言）

对 OpenCode 说：
```
记录：张三今天Review了我的代码，提出了很好的优化建议
```

OpenCode 会自动追加到 `张三-时间轴.md` 顶部。

#### 场景2：查询信息

**直接打开文件查看**：
- 双击 `张三-时间轴.md`，直观看到完整时间线

**或通过 OpenCode 查询**：
```
帮我看看张三最近的表现
```

```
生成张三的年终总结
```

```
准备明天和张三的1对1
```

```
这周团队整体状态怎么样
```

### 第四步：数据同步到网盘（可选，1分钟）

**方案A - 使用 Dropbox/坚果云客户端：**
1. 安装网盘客户端
2. 创建软链接：
```powershell
# 示例：同步到 Dropbox
cmd /c mklink /J "$env:USERPROFILE\Dropbox\team-memory" "$env:USERPROFILE\.config\opencode\skills\team-memory\data"
```

**方案B - 手动备份：**
每周复制一次数据文件夹到网盘

---

## 日常使用模板

### 每日记录（2-3分钟）

每天早上或下班前，花几分钟记录：

```
记录：
- 张三主动修复了生产bug，响应很快
- 李四在会议上提出了很好的架构建议
- 王五这周有点沉默，可能需要关注
```

### 每周五复盘（5分钟）

```
生成本周的团队观察报告
```

系统会输出：
- 本周亮点汇总
- 需关注的事项
- 下周建议

### 月度回顾（10分钟）

```
生成本月的团队趋势分析
对比上个月的变化
```

### 关键场景使用

#### 写推荐信前
```
帮我写一封张三的推荐信草稿，用于申请高级工程师
```

#### 年终总结前
```
生成张三2024年的完整绩效评估
包含具体数据和案例
```

#### 1:1沟通前
```
准备明天和张三的1对1谈话
重点关注他最近的项目表现
```

#### 晋升评估时
```
对比张三和李四的晋升资格
从技术能力和团队贡献两个维度
```

---

## 文件结构说明

```
~/.config/opencode/skills/team-memory/
├── SKILL.md                    # Skill 定义（精简，90行）
├── skill-config.yaml           # 团队配置（编辑这个）
├── references/                # 详细参考文档
│   ├── 场景示例.md
│   ├── 记录模板.md
│   └── 故障排除.md
├── scripts/                   # 初始化脚本
│   ├── init.sh
│   └── new-member.sh
└── data/                      # 数据目录
    ├── members/               # 成员时间轴
    ├── manager-journal/       # 管理反思
    │   └── tracker/          # 自动追踪
    └── insights/              # 洞察分析
```

---

## 输入格式速查

### 基础格式
```
记录 [姓名] [时间] [事件描述]
```

### 时间词
- 今天、昨天、前天
- 本周、上周
- 月初、月中、月底
- Q1、Q2、Q3、Q4
- 具体日期：1月15日、2024-01-15

### 类别词（自动分类）
**技术能力**：
- 技术突破、代码质量、架构设计、性能优化
- bug修复、技术分享、学习新技能

**协作沟通**：
- 沟通问题、主动分享、帮助同事、跨组协作
- 会议表现、文档撰写

**项目交付**：
- 项目交付、客户反馈、owner意识
- 提前完成、延期风险、需求变更

**团队影响**：
- 知识分享、流程改进、带新人
- 文化建设、团队活动

### 评级词（可选）
- 优秀/出色/超预期
- 良好/不错
- 一般/正常
- 需关注/问题

---

## 常见问题

### Q1：我可以记录负面观察吗？
**可以**，但要注意：
- 记录事实而非主观判断
- 示例："今天会议上打断同事3次" ✅ vs "沟通能力差" ❌
- 同时记录正面表现，保持平衡

### Q2：记录会被人看到吗？
**不会**，数据完全本地存储：
- 存储在你的电脑 `~/.config/opencode/skills/team-memory/`
- 不上传到任何云端（除非你手动同步到网盘）
- OpenCode 官方也无法访问

### Q3：如果换电脑怎么办？
**方法1**：复制整个 `team-memory` 文件夹到新电脑
**方法2**：使用网盘同步（推荐 Dropbox/坚果云）
**方法3**：定期导出备份

### Q4：记录太多会不会很慢？
**不会**：
- Markdown 文件搜索很快
- 可按时间段归档旧数据
- OpenCode 会自动加载最近3个月的记录

### Q5：可以修改历史记录吗？
**可以**：
- 直接编辑 `data/members/member-XXX.md` 文件
- 但建议保留原始记录，新增补充说明

### Q6：如何删除某个成员的数据？
1. 移动到 `data/archive/` 目录（保留历史）
2. 或从 `skill-config.yaml` 中移除该成员

---

## 进阶技巧

### 1. 批量导入历史记录

如果你有 Excel 或笔记中的历史观察，可以批量转换：

```python
# 示例：将 Excel 转换为 Markdown
import pandas as pd
from datetime import datetime

# 读取 Excel
df = pd.read_excel('history.xlsx')

# 转换为 Markdown 格式
for _, row in df.iterrows():
    member_id = f"member-{row['编号']:03d}"
    date = row['日期'].strftime('%Y-%m-%d')
    content = row['内容']
    
    md_content = f"""---
timestamp: {date}T09:00:00
member-id: {member_id}
categories: []
rating: positive
---

## 原始记录
{content}
"""
    
    # 写入文件
    with open(f'members/{member_id}.md', 'a', encoding='utf-8') as f:
        f.write(md_content + '\n---\n')
```

### 2. 自定义输出模板

在 `data/templates/` 创建新模板：

**annual-review-custom.md**：
```markdown
# {{name}} {{year}}年度评估

## 基本信息
- 姓名：{{name}}
- 职级：{{level}}
- 入职时间：{{join-date}}
- 评估周期：{{period}}

## 关键成就
{{achievements}}

## 发展建议
{{suggestions}}

## 晋升建议
{{promotion-recommendation}}
```

### 3. 集成到工作流

**晨会前**：
```
看看今天谁需要我重点关注
```

**周会前**：
```
生成本周的团队亮点和需要支持的事项
```

**月度规划**：
```
基于上个月的表现，帮我制定下个月的管理重点
```

---

## 隐私保护检查清单

- [ ] 仅使用编号（member-001）在记录文件中
- [ ] 真名映射存储在本地配置文件
- [ ] 不上传到公共 Git 仓库
- [ ] 网盘同步使用加密（可选）
- [ ] 定期审查记录内容，删除敏感信息
- [ ] 离职成员数据及时归档

---

## 反馈和改进

使用1-2周后，建议回顾：

1. **记录频率**：每天能记录几条？是否可持续？
2. **最有用的输出**：年终总结、1:1准备、还是周报？
3. **需要调整的**：分类标签是否合适？输出格式是否需要改？
4. **新场景**：是否有新的使用场景可以支持？

---

**现在就开始**：
1. 执行安装命令
2. 配置你的9个成员
3. 记录今天的第一个观察
4. 让 OpenCode 帮你生成第一份报告

有问题随时问我！
