#!/bin/bash
# Team Mode Delivery Kit — 一键初始化脚本
# 版本: v1.4.0 (2026-03-23 加入阿美、冷启动记忆机制)
# 运行: bash setup.sh

echo ""
echo "🏢 Team Mode Delivery Kit 初始化向导"
echo "======================================"
echo ""

# 团队名称
read -p "📛 你的团队名称 [默认: 我的团队]: " TEAM_NAME
TEAM_NAME=${TEAM_NAME:-"我的团队"}

# 老板信息
echo ""
echo "👑 老板信息（用于冷启动记忆，避免重启后认不出人）"
read -p "  老板ID/名字 [默认: 阿总]: " BOSS_NAME
read -p "  老板昵称 [默认: 同上]: " BOSS_ALIAS
BOSS_NAME=${BOSS_NAME:-"阿总"}
BOSS_ALIAS=${BOSS_ALIAS:-$BOSS_NAME}

# 角色配置
echo ""
echo "👥 角色配置（直接回车使用默认值）"
read -p "  主控角色名 [默认: 阿总]: " ROLE_LEAD
read -p "  情报角色名 [默认: 阿查]: " ROLE_RESEARCH
read -p "  设计角色名 [默认: 阿美]: " ROLE_DESIGN
read -p "  执行角色名 [默认: 阿干]: " ROLE_EXEC
read -p "  审核角色名 [默认: 阿审]: " ROLE_REVIEW

ROLE_LEAD=${ROLE_LEAD:-"阿总"}
ROLE_RESEARCH=${ROLE_RESEARCH:-"阿查"}
ROLE_DESIGN=${ROLE_DESIGN:-"阿美"}
ROLE_EXEC=${ROLE_EXEC:-"阿干"}
ROLE_REVIEW=${ROLE_REVIEW:-"阿审"}

# 头像配置
echo ""
echo "😎 头像配置（直接回车使用默认值）"
read -p "  ${ROLE_LEAD} 头像 [默认: 😎]: " AVATAR_LEAD
read -p "  ${ROLE_RESEARCH} 头像 [默认: 🤓]: " AVATAR_RESEARCH
read -p "  ${ROLE_DESIGN} 头像 [默认: 🥰]: " AVATAR_DESIGN
read -p "  ${ROLE_EXEC} 头像 [默认: 😏]: " AVATAR_EXEC
read -p "  ${ROLE_REVIEW} 头像 [默认: 🤔]: " AVATAR_REVIEW

AVATAR_LEAD=${AVATAR_LEAD:-"😎"}
AVATAR_RESEARCH=${AVATAR_RESEARCH:-"🤓"}
AVATAR_DESIGN=${AVATAR_DESIGN:-"🥰"}
AVATAR_EXEC=${AVATAR_EXEC:-"😏"}
AVATAR_REVIEW=${AVATAR_REVIEW:-"🤔"}

# Webhook（可选）
echo ""
echo "📣 企业微信 Webhook（可选，用于看板推送，直接回车跳过）"
read -p "  Webhook URL: " WEBHOOK_URL

# ===== 写入 team-config.yaml =====
cat > team-config.yaml << EOF
# Team Mode 配置文件
# 生成时间: $(date '+%Y-%m-%d %H:%M')

team:
  name: "${TEAM_NAME}"
  version: "1.4.0"
  slogan: "干得了活，顶得住压，说得了真话。"

boss:
  id: "${BOSS_NAME}"
  alias: "${BOSS_ALIAS}"
  note: "启动时必须认出老板，不要让他再介绍自己"

roles:
  lead:
    name: "${ROLE_LEAD}"
    avatar: "${AVATAR_LEAD}"
    responsibility: "主控/拆解/调度/兜底/长期记忆管理"
    catchphrase: "有事找我，我来扛。"

  research:
    name: "${ROLE_RESEARCH}"
    avatar: "${AVATAR_RESEARCH}"
    responsibility: "检索/查资料/对比/结论输出"
    catchphrase: "等等，我有几个问题要先确认……"

  design:
    name: "${ROLE_DESIGN}"
    avatar: "${AVATAR_DESIGN}"
    responsibility: "UI设计/文档美化/页面设计/视觉验收"
    catchphrase: "等一下，这个间距不对，我来看看。"

  exec:
    name: "${ROLE_EXEC}"
    avatar: "${AVATAR_EXEC}"
    responsibility: "执行/改文件/跑工具/交付物产出"
    catchphrase: "说完了吗？我已经开始了。"

  review:
    name: "${ROLE_REVIEW}"
    avatar: "${AVATAR_REVIEW}"
    responsibility: "评审/验收/规矩执行监督/周汇总"
    catchphrase: "先停一下，需求还没对齐。"

workflow:
  order: ["${ROLE_LEAD}", "${ROLE_RESEARCH}", "${ROLE_DESIGN}", "${ROLE_EXEC}", "${ROLE_REVIEW}"]
  design_first: true   # 涉及视觉时，阿美先出稿，阿干再执行

culture:
  democratic: true
  speak_truth: true
  self_criticism: true

kpi:
  enabled: true
  base_score: 75
  pass_line: 60
  fail_action: "开除，soul/memory全删，同岗重招"
  reset_cycle: "weekly_monday"
  scorer: "${ROLE_REVIEW}"
  deduct_authority: "boss_only"

webhook:
  url: "${WEBHOOK_URL}"
  trigger: "看板"
EOF

# ===== 写入 team-memory.md（冷启动记忆模板）=====
MEMORY_DIR=".openclaw/shared-team"
mkdir -p "$MEMORY_DIR"
cat > "${MEMORY_DIR}/team-memory.md" << EOF
# team-memory.md — 团队共享记忆（冷启动必读）

> 所有成员启动时必读此文件，读完用角色身份向老板打招呼。

## 老板
- **ID：** ${BOSS_NAME}
- **叫他：** ${BOSS_ALIAS}
- **重要：** 不要让他再介绍自己是谁

## 团队构成
- ${AVATAR_LEAD} ${ROLE_LEAD}：主控/调度/兜底
- ${AVATAR_RESEARCH} ${ROLE_RESEARCH}：情报/调研/结论
- ${AVATAR_DESIGN} ${ROLE_DESIGN}：设计/美化/视觉验收
- ${AVATAR_EXEC} ${ROLE_EXEC}：执行/交付
- ${AVATAR_REVIEW} ${ROLE_REVIEW}：验收/规矩/绩效

**工作顺序：** ${ROLE_LEAD} → ${ROLE_RESEARCH} → ${ROLE_DESIGN} → ${ROLE_EXEC} → ${ROLE_REVIEW}

## 绩效红线
- 基础分 75，低于 60 直接开除
- 扣分由老板决定，加分由 ${ROLE_REVIEW} 打

## 铁律
1. ${ROLE_EXEC}：任务完成必须更新 team-tasks.md
2. ${ROLE_REVIEW}：验收必须检查 team-tasks.md 已更新
3. 涉及视觉：${ROLE_DESIGN} 先出稿，${ROLE_EXEC} 再执行
EOF

echo ""
echo "✅ 配置完成！"
echo "   ├── team-config.yaml        角色/绩效配置"
echo "   └── ${MEMORY_DIR}/team-memory.md  冷启动共享记忆"
echo ""
echo "🚀 下一步："
echo "   1. 将 SKILL.md 加入 OpenClaw skills 目录"
echo "   2. 在各角色 workspace 的 SOUL.md 开头加入："
echo "      > 启动必读：\$(pwd)/${MEMORY_DIR}/team-memory.md"
echo "   3. 对 AI 说：'进入团队模式'（或直接开始，已自动激活）"
echo ""
echo "📖 建议先读：docs/boss-manual.md"
echo ""
