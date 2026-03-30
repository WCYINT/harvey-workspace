#!/usr/bin/env python3

import argparse
import csv
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

SCHEDULES_DIR = Path("schedules")
FIELDS = ["id", "task", "deadline", "priority", "reminder", "note"]
CHAT_ID_PATTERN = re.compile(r'^[A-Za-z0-9._-]+$')
VALID_PRIORITIES = {"P0", "P1", "P2", "P3"}
PRIORITY_LABELS = {
    "P0": "P0 — 重要且紧急",
    "P1": "P1 — 紧急不重要",
    "P2": "P2 — 重要不紧急",
    "P3": "P3 — 不重要不紧急",
}
WEEKDAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def validate_chat_id(chat_id):
    if not chat_id or not CHAT_ID_PATTERN.match(chat_id):
        print(f"错误: chat_id 包含非法字符，仅允许字母、数字、点、下划线和连字符: {chat_id}")
        sys.exit(1)


def get_csv_path(chat_id):
    validate_chat_id(chat_id)
    csv_path = (SCHEDULES_DIR / f"{chat_id}.csv").resolve()
    schedules_root = SCHEDULES_DIR.resolve()
    if not csv_path.is_relative_to(schedules_root):
        print(f"错误: 非法路径: {chat_id}")
        sys.exit(1)
    return csv_path


def ensure_csv(csv_path):
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    if not csv_path.exists():
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()


def read_all(csv_path):
    ensure_csv(csv_path)
    with open(csv_path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_all(csv_path, rows):
    ensure_csv(csv_path)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def next_id(rows):
    if not rows:
        return 1
    return max(int(r["id"]) for r in rows) + 1


def reindex(rows):
    for i, r in enumerate(rows, 1):
        r["id"] = str(i)
    return rows


def format_deadline_short(deadline_str):
    if not deadline_str:
        return "无DDL"
    try:
        if len(deadline_str) > 10:
            dt = datetime.strptime(deadline_str, "%Y-%m-%d %H:%M")
            wd = WEEKDAYS[dt.weekday()]
            return f"{dt.month}/{dt.day}({wd}) {dt.strftime('%H:%M')}"
        else:
            dt = datetime.strptime(deadline_str, "%Y-%m-%d")
            wd = WEEKDAYS[dt.weekday()]
            return f"{dt.month}/{dt.day}({wd})"
    except ValueError:
        return deadline_str


def parse_deadline(deadline_str):
    if not deadline_str:
        return None
    try:
        if len(deadline_str) > 10:
            return datetime.strptime(deadline_str, "%Y-%m-%d %H:%M")
        else:
            return datetime.strptime(deadline_str, "%Y-%m-%d")
    except ValueError:
        return None


def next_month_range(now):
    if now.month == 12:
        return now.replace(year=now.year + 1, month=1, day=1)
    return now.replace(month=now.month + 1, day=1)


def filter_rows(rows, today=False, tomorrow=False, week=False, next_week=False,
                month=False, next_month=False, priority=None):
    now = datetime.now()
    result = rows

    if priority:
        result = [r for r in result if r["priority"] == priority]

    if today:
        target = now.strftime("%Y-%m-%d")
        result = [r for r in result if r["deadline"].startswith(target)]
    elif tomorrow:
        target = (now + timedelta(days=1)).strftime("%Y-%m-%d")
        result = [r for r in result if r["deadline"].startswith(target)]
    elif week:
        week_start = now - timedelta(days=now.weekday())
        week_end = week_start + timedelta(days=6)
        result = [r for r in result
                  if (dt := parse_deadline(r["deadline"])) and week_start.date() <= dt.date() <= week_end.date()]
    elif next_week:
        nw_start = now - timedelta(days=now.weekday()) + timedelta(weeks=1)
        nw_end = nw_start + timedelta(days=6)
        result = [r for r in result
                  if (dt := parse_deadline(r["deadline"])) and nw_start.date() <= dt.date() <= nw_end.date()]
    elif month:
        result = [r for r in result
                  if (dt := parse_deadline(r["deadline"])) and dt.year == now.year and dt.month == now.month]
    elif next_month:
        nm_first = next_month_range(now)
        result = [r for r in result
                  if (dt := parse_deadline(r["deadline"])) and dt.year == nm_first.year and dt.month == nm_first.month]

    return result


def format_list(rows, title="日程表"):
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d %H:%M")

    lines = []
    lines.append("━━━━━━━━━━━━━━━━")
    lines.append(f"  {title}  |  {date_str} 更新")
    lines.append("━━━━━━━━━━━━━━━━")

    counts = {"P0": 0, "P1": 0, "P2": 0, "P3": 0}

    for p in ["P0", "P1", "P2", "P3"]:
        lines.append("")
        lines.append(PRIORITY_LABELS[p])
        lines.append("────────────────")

        p_rows = [r for r in rows if r["priority"] == p]
        counts[p] = len(p_rows)

        if not p_rows:
            lines.append("  (暂无)")
        else:
            for i, r in enumerate(p_rows, 1):
                ddl = format_deadline_short(r["deadline"])
                reminder_mark = " [已设提醒]" if r.get("reminder") == "Y" else ""
                lines.append(f"  {i}. {r['task']}{reminder_mark}")
                lines.append(f"     DDL: {ddl}")
                if r.get("note"):
                    lines.append(f"     备注: {r['note']}")

    total = sum(counts.values())
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━")
    stats = "  ".join(f"{k}:{v}" for k, v in counts.items())
    lines.append(f"  共 {total} 项  {stats}")
    lines.append("━━━━━━━━━━━━━━━━")

    return "\n".join(lines)


def cmd_add(args):
    if args.priority not in VALID_PRIORITIES:
        print(f"错误: 优先级必须是 P0/P1/P2/P3，收到: {args.priority}")
        sys.exit(1)

    csv_path = get_csv_path(args.chat_id)
    rows = read_all(csv_path)
    new_row = {
        "id": str(next_id(rows)),
        "task": args.task,
        "deadline": args.deadline or "",
        "priority": args.priority,
        "reminder": "N",
        "note": args.note or "",
    }
    rows.append(new_row)
    write_all(csv_path, rows)
    print(f"已添加任务 #{new_row['id']} 到 {args.priority}: {args.task}")


def cmd_list(args):
    csv_path = get_csv_path(args.chat_id)
    rows = read_all(csv_path)

    if args.today:
        rows = filter_rows(rows, today=True)
        title = "今日日程"
    elif args.tomorrow:
        rows = filter_rows(rows, tomorrow=True)
        title = "明日日程"
    elif args.week:
        rows = filter_rows(rows, week=True)
        title = "本周日程"
    elif args.next_week:
        rows = filter_rows(rows, next_week=True)
        title = "下周日程"
    elif args.month:
        rows = filter_rows(rows, month=True)
        title = "本月日程"
    elif args.next_month:
        rows = filter_rows(rows, next_month=True)
        title = "下月日程"
    elif args.priority:
        rows = filter_rows(rows, priority=args.priority)
        title = f"{PRIORITY_LABELS.get(args.priority, args.priority)} 日程"
    else:
        title = "日程表"

    print(format_list(rows, title))


def cmd_update(args):
    csv_path = get_csv_path(args.chat_id)
    rows = read_all(csv_path)
    target = None
    for r in rows:
        if r["id"] == str(args.id):
            target = r
            break

    if not target:
        print(f"错误: 未找到 ID={args.id} 的任务")
        sys.exit(1)

    updated = []
    if args.task is not None:
        target["task"] = args.task
        updated.append("任务名")
    if args.deadline is not None:
        target["deadline"] = args.deadline
        updated.append("截止时间")
    if args.priority is not None:
        if args.priority not in VALID_PRIORITIES:
            print(f"错误: 优先级必须是 P0/P1/P2/P3，收到: {args.priority}")
            sys.exit(1)
        target["priority"] = args.priority
        updated.append("优先级")
    if args.reminder is not None:
        target["reminder"] = args.reminder
        updated.append("提醒")
    if args.note is not None:
        target["note"] = args.note
        updated.append("备注")

    if not updated:
        print("错误: 未指定要更新的字段")
        sys.exit(1)

    write_all(csv_path, rows)
    fields = "、".join(updated)
    print(f"已更新任务 #{args.id}「{target['task']}」的{fields}")


def cmd_delete(args):
    csv_path = get_csv_path(args.chat_id)
    rows = read_all(csv_path)
    target = None
    for r in rows:
        if r["id"] == str(args.id):
            target = r
            break

    if not target:
        print(f"错误: 未找到 ID={args.id} 的任务")
        sys.exit(1)

    task_name = target["task"]
    rows = [r for r in rows if r["id"] != str(args.id)]
    rows = reindex(rows)
    write_all(csv_path, rows)
    print(f"已删除任务「{task_name}」，剩余 {len(rows)} 项")


def main():
    parser = argparse.ArgumentParser(description="日程表 CRUD")
    sub = parser.add_subparsers(dest="command", required=True)

    # add
    p_add = sub.add_parser("add")
    p_add.add_argument("--chat-id", required=True)
    p_add.add_argument("--task", required=True)
    p_add.add_argument("--deadline", default="")
    p_add.add_argument("--priority", required=True)
    p_add.add_argument("--note", default="")

    # list
    p_list = sub.add_parser("list")
    p_list.add_argument("--chat-id", required=True)
    p_list.add_argument("--today", action="store_true")
    p_list.add_argument("--tomorrow", action="store_true")
    p_list.add_argument("--week", action="store_true")
    p_list.add_argument("--next-week", action="store_true")
    p_list.add_argument("--month", action="store_true")
    p_list.add_argument("--next-month", action="store_true")
    p_list.add_argument("--priority", default=None)

    # update
    p_update = sub.add_parser("update")
    p_update.add_argument("--chat-id", required=True)
    p_update.add_argument("--id", type=int, required=True)
    p_update.add_argument("--task", default=None)
    p_update.add_argument("--deadline", default=None)
    p_update.add_argument("--priority", default=None)
    p_update.add_argument("--reminder", default=None)
    p_update.add_argument("--note", default=None)

    # delete
    p_delete = sub.add_parser("delete")
    p_delete.add_argument("--chat-id", required=True)
    p_delete.add_argument("--id", type=int, required=True)

    args = parser.parse_args()

    if args.command == "add":
        cmd_add(args)
    elif args.command == "list":
        cmd_list(args)
    elif args.command == "update":
        cmd_update(args)
    elif args.command == "delete":
        cmd_delete(args)


if __name__ == "__main__":
    main()
