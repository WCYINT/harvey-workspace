# MBA论文修改技能安装指南

## 安装方法

### 方法一：直接复制到技能目录
```bash
# 复制技能到OpenClaw技能目录
cp -r /path/to/mba-thesis /root/.nvm/versions/node/v22.22.0/lib/node_modules/openclaw/skills/
```

### 方法二：使用skill-creator工具
```bash
# 进入技能目录
cd /root/.openclaw/workspace/skills/mba-thesis

# 使用skill-creator打包
python3 /root/.nvm/versions/node/v22.22.0/lib/node_modules/openclaw/skills/skill-creator/scripts/package_skill.py .

# 安装生成的.skill文件
openclaw skills install mba-thesis.skill
```

## 技能结构
```
mba-thesis/
├── SKILL.md                    # 主技能文件
├── templates/                  # 模板文件
│   ├── mba-thesis-structure.md # 论文结构模板
│   └── checklist.md           # 检查清单
├── scripts/                   # 工具脚本
│   └── word_count.py         # 字数统计工具
└── references/               # 参考资料
    └── academic_writing_tips.md # 学术写作技巧
```

## 使用前准备

### 1. 安装Python依赖
```bash
pip install python-docx PyPDF2 pandoc
```

### 2. 设置环境变量（可选）
```bash
# 添加技能路径
export OPENCLAW_SKILLS_PATH="/root/.nvm/versions/node/v22.22.0/lib/node_modules/openclaw/skills"
```

## 使用方法

### 1. 启动OpenClaw
```bash
openclaw start
```

### 2. 触发技能
当讨论MBA论文修改时，技能会自动触发。

### 3. 使用技能功能
- 提供论文文件进行分析
- 使用检查清单
- 应用写作技巧
- 使用字数统计工具

## 测试技能

### 1. 测试字数统计工具
```bash
python3 scripts/word_count.py your_thesis.txt
```

### 2. 测试技能触发
在OpenClaw会话中讨论MBA论文修改话题。

## 常见问题

### Q: 技能没有触发？
A: 确保技能已正确安装到技能目录，并检查SKILL.md中的description字段。

### Q: 工具脚本无法运行？
A: 检查Python环境，确保已安装所需依赖。

### Q: 如何自定义技能？
A: 编辑SKILL.md和相关文件，根据具体需求调整内容。

## 更新技能
```bash
# 重新打包
python3 package_skill.py .

# 重新安装
openclaw skills install mba-thesis.skill --force
```

## 支持格式
- 文本文件：.txt, .md
- Word文档：.docx
- PDF文件：.pdf（需要PyPDF2）

## 注意事项
1. 技能仅提供修改建议，不代写论文
2. 保持学术诚信，正确引用
3. 根据学校具体要求调整