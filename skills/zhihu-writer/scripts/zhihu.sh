#!/usr/bin/env bash
# 知乎内容创作助手 — Zhihu Writer
# Usage: bash zhihu.sh <command> [input]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PY_SCRIPT="$SCRIPT_DIR/zhihu_gen.py"

if [ ! -f "$PY_SCRIPT" ]; then
    echo "Error: zhihu_gen.py not found at $PY_SCRIPT"
    exit 1
fi

CMD="${1:-help}"
shift 2>/dev/null || true
INPUT="$*"

case "$CMD" in
    help|--help|-h)
        python3 "$PY_SCRIPT" --help 2>/dev/null || cat << 'HELPEOF'
知乎内容创作助手

Usage: bash zhihu.sh <command> [topic/input]

Commands:
  answer <topic>      生成知乎高赞回答
  article <topic>     生成知乎专栏文章
  title <topic>       生成吸睛标题（5个备选）
  structure <topic>   设计回答结构大纲
  topic <niche>       推荐热门话题选题
  growth              账号成长策略
  seo <topic>         知乎SEO优化建议
  analyze <url>       分析高赞回答结构

Examples:
  bash zhihu.sh answer "如何看待AI替代程序员"
  bash zhihu.sh article "2026年最值得学的编程语言"
  bash zhihu.sh title "远程工作"
  bash zhihu.sh topic "科技"

Powered by BytesAgain | bytesagain.com | hello@bytesagain.com
HELPEOF
        ;;
    *)
        if [ -z "$INPUT" ]; then
            echo "Error: 请提供主题或内容"
            echo "Usage: bash zhihu.sh $CMD <topic>"
            exit 1
        fi
        python3 "$PY_SCRIPT" "$CMD" "$INPUT"
        ;;
esac
