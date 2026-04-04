#!/bin/bash

# Team Memory - 创建新成员完整档案
# 用法: bash new-member.sh [姓名] [角色] [入职日期]
# 示例: bash new-member.sh 张三 后端开发工程师 2023-03-15

set -e

SKILL_DIR="$HOME/.config/opencode/skills/team-memory"
MEMBERS_DIR="$SKILL_DIR/data/members"

# 检查参数
if [ -z "$1" ]; then
    echo "❌ 用法: bash new-member.sh [姓名] [角色] [入职日期]"
    echo "   示例: bash new-member.sh 张三 后端开发 2023-03-15"
    exit 1
fi

NAME="$1"
ROLE="${2:-职位未填写}"
JOIN_DATE="${3:-$(date +%Y-%m-%d)}"

# 生成文件名
PROFILE_FILE="$MEMBERS_DIR/$NAME-档案.md"
TIMELINE_FILE="$MEMBERS_DIR/$NAME-时间轴.md"
DISTILL_FILE="$MEMBERS_DIR/$NAME-蒸馏.md"

# 检查是否已存在
if [ -f "$PROFILE_FILE" ]; then
    echo "⚠️  文件已存在: $PROFILE_FILE"
    read -p "是否覆盖? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ 已取消"
        exit 1
    fi
fi

# 生成成员ID
MEMBER_COUNT=$(ls -1 "$MEMBERS_DIR"/*-档案.md 2>/dev/null | wc -l || echo "0")
MEMBER_ID=$(printf "member-%03d" $((MEMBER_COUNT + 1)))

echo "📝 创建成员档案..."
echo "   姓名: $NAME"
echo "   角色: $ROLE"
echo "   入职: $JOIN_DATE"
echo "   ID: $MEMBER_ID"

# 创建档案文件
cat > "$PROFILE_FILE" << EOF
# $NAME - 档案

## 基本信息
**成员ID**: $MEMBER_ID  
**角色**: $ROLE  
**入职时间**: $JOIN_DATE  
**所属团队**: 

---

## 性格类型
**FFS类型**: 
**特点**: 
**管理策略**: 

---

## 本年度 OKR

### O1: 核心业务与业绩
**目标**: 保障产出的"质"与"量"，提升业务转化效率

**KR**:
- [ ] KR1: (完成度: 0%)
- [ ] KR2: (完成度: 0%)

**季度进度**:
| 季度 | 进度 | 指导方向 |
|------|------|----------|
| Q1 | - | |
| Q2 | - | |
| Q3 | - | |
| Q4 | - | |

---

### O2: 影棚建设与技术沉淀
**目标**: 优化作业环境，沉淀技术资产

**KR**:
- [ ] KR1: (完成度: 0%)

**季度进度**:
| 季度 | 进度 | 指导方向 |
|------|------|----------|
| Q1 | - | |
| Q2 | - | |
| Q3 | - | |
| Q4 | - | |

---

### O3: 团队赋能与协作
**目标**: 激活团队战力，提升协同效率

**KR**:
- [ ] KR1: (完成度: 0%)

**季度进度**:
| 季度 | 进度 | 指导方向 |
|------|------|----------|
| Q1 | - | |
| Q2 | - | |
| Q3 | - | |
| Q4 | - | |

---

### O4: 个人专业成长
**目标**: 构建不可替代的个人核心竞争力

**KR**:
- [ ] KR1: (完成度: 0%)

**季度进度**:
| 季度 | 进度 | 指导方向 |
|------|------|----------|
| Q1 | - | |
| Q2 | - | |
| Q3 | - | |
| Q4 | - | |

---

## 个人发展计划

### 短期目标（3个月）
- [ ] 

### 中期目标（6个月）
- [ ] 

### 长期目标（1年）
- [ ] 

---

## 历史OKR
<!-- 每年结束后归档 -->

*创建于 $JOIN_DATE*
EOF

# 创建时间轴文件
cat > "$TIMELINE_FILE" << EOF
# $NAME - 团队记忆时间轴

> **成员ID**: $MEMBER_ID  
> **角色**: $ROLE  
> **入职时间**: $JOIN_DATE  
> **所属团队**: 

## 📍 快速定位
**最近状态**:   
**重点关注**:   
**下次1:1**:   
**标签云**: 

---

## 🕐 时间轴（从新到旧）

<!-- 从这里开始添加记录 -->

---

*创建于 $JOIN_DATE*
EOF

# 创建蒸馏文件
cat > "$DISTILL_FILE" << EOF
# $NAME - 蒸馏

## 一句话画像
{技术特点}、{性格特点}、{注意点}

## 性格
{FFS类型}

## 本季OKR进度
- O1: 业务与业绩 [待定]
- O2: 技术沉淀 [待定]
- O3: 团队协作 [待定]
- O4: 个人成长 [待定]

## 追踪项
<!-- 记录后添加 -->

## 我的承诺
<!-- 记录后添加 -->

#档案: $NAME-档案.md
#时间轴: $NAME-时间轴.md
EOF

echo ""
echo "✅ 已创建:"
echo "   📄 $PROFILE_FILE"
echo "   📄 $TIMELINE_FILE"
echo "   📄 $DISTILL_FILE"
echo ""
echo "📝 下一步:"
echo "   1. 编辑档案文件完善性格和OKR"
echo "   2. 沟通年度OKR后更新档案"
echo "   3. 更新 skill-config.yaml 添加成员映射"
echo ""
