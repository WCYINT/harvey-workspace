#!/bin/bash

# Team Memory - 初始化脚本
# 用法: bash init.sh

set -e

SKILL_DIR="$HOME/.config/opencode/skills/team-memory"

echo "🚀 Team Memory 初始化..."

# 创建目录结构
echo "📁 创建目录结构..."
mkdir -p "$SKILL_DIR/data/members"
mkdir -p "$SKILL_DIR/data/insights"
mkdir -p "$SKILL_DIR/data/templates"
mkdir -p "$SKILL_DIR/data/archive"
mkdir -p "$SKILL_DIR/data/manager-journal/tracker/pending"
mkdir -p "$SKILL_DIR/data/manager-journal/tracker/completed"
mkdir -p "$SKILL_DIR/data/manager-journal/tracker/summary"
mkdir -p "$SKILL_DIR/data/manager-journal/月度复盘"

# 复制配置文件（如果不存在）
if [ ! -f "$SKILL_DIR/skill-config.yaml" ]; then
    if [ -f "$HOME/Desktop/team-memory/skill-config.example.yaml" ]; then
        echo "📋 复制示例配置文件..."
        cp "$HOME/Desktop/team-memory/skill-config.example.yaml" "$SKILL_DIR/skill-config.yaml"
        echo "⚠️  请编辑 $SKILL_DIR/skill-config.yaml 配置你的团队"
    else
        echo "⚠️  未找到配置文件，请手动创建"
    fi
fi

# 创建 .gitkeep 文件（保持目录结构）
touch "$SKILL_DIR/data/members/.gitkeep"
touch "$SKILL_DIR/data/insights/.gitkeep"
touch "$SKILL_DIR/data/templates/.gitkeep"
touch "$SKILL_DIR/data/archive/.gitkeep"

echo ""
echo "✅ 初始化完成！"
echo ""
echo "📁 目录结构:"
echo "   $SKILL_DIR/"
echo "   ├── data/"
echo "   │   ├── members/"
echo "   │   ├── insights/"
echo "   │   ├── templates/"
echo "   │   ├── archive/"
echo "   │   └── manager-journal/"
echo "   │       └── tracker/"
echo "   └── skill-config.yaml"
echo ""
echo "📝 下一步:"
echo "   1. 编辑 skill-config.yaml 配置你的团队"
echo "   2. 复制模板创建成员时间轴"
echo "   3. 开始使用！"
echo ""
