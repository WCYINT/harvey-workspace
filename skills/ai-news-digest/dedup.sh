#!/bin/bash
# AI News Digest — Dedup Tracker Manager
# Usage: dedup.sh {show|clean|reset|add} [args]

set -euo pipefail

DEDUP_FILE="${DEDUP_DIR:-data}/news-sent.txt"
mkdir -p "$(dirname "$DEDUP_FILE")"
touch "$DEDUP_FILE"

case "${1:-show}" in
  show)
    DAYS="${2:-7}"
    echo "=== Stories sent in last ${DAYS} days ==="
    CUTOFF=$(date -d "-${DAYS} days" '+%Y-%m-%d' 2>/dev/null || date -v-${DAYS}d '+%Y-%m-%d')
    awk -F'|' -v cutoff="$CUTOFF" '$1 >= cutoff' "$DEDUP_FILE" | sort -r
    echo ""
    echo "Total: $(awk -F'|' -v cutoff="$CUTOFF" '$1 >= cutoff' "$DEDUP_FILE" | wc -l) stories"
    ;;
  
  clean)
    DAYS="${2:-7}"
    CUTOFF=$(date -d "-${DAYS} days" '+%Y-%m-%d' 2>/dev/null || date -v-${DAYS}d '+%Y-%m-%d')
    BEFORE=$(wc -l < "$DEDUP_FILE")
    awk -F'|' -v cutoff="$CUTOFF" '$1 >= cutoff' "$DEDUP_FILE" > "${DEDUP_FILE}.tmp"
    mv "${DEDUP_FILE}.tmp" "$DEDUP_FILE"
    AFTER=$(wc -l < "$DEDUP_FILE")
    echo "Cleaned: removed $((BEFORE - AFTER)) old entries (kept last ${DAYS} days)"
    ;;
  
  reset)
    echo "Resetting dedup tracker..."
    > "$DEDUP_FILE"
    echo "✅ Tracker cleared"
    ;;
  
  add)
    shift
    DATE=$(date '+%Y-%m-%d')
    for headline in "$@"; do
      echo "${DATE}|${headline}" >> "$DEDUP_FILE"
    done
    echo "Added $# stories to tracker"
    ;;
  
  *)
    echo "Usage: dedup.sh {show|clean|reset|add} [args]"
    echo "  show [days]   — Show stories from last N days (default 7)"
    echo "  clean [days]  — Remove entries older than N days (default 7)"
    echo "  reset         — Clear all entries"
    echo "  add \"headline\" — Add story to tracker"
    ;;
esac
