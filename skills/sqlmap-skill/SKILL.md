---
name: sqlmap-skill
description: Build, explain, and run authorized sqlmap assessments for SQL injection testing from URL, raw HTTP request files, proxy logs, or batch target lists. Use when a user asks to detect SQL injection, fingerprint DBMS, enumerate schema/data, dump records, tune request/auth/proxy/tamper options, or map a testing goal to concrete sqlmap flags.
---

# Sqlmap Operator

## Overview

Translate user testing goals into correct sqlmap commands and execute them in a controlled way.
Use this skill to choose flags, run staged scans, and return findings with reproducible command lines.

## Workflow

1. Ask for `sqlmap_cmd` before generating commands.
Default to `sqlmap` when user does not provide a path.
Accept examples like `python /opt/sqlmap/sqlmap.py` or `python C:\tools\sqlmap\sqlmap.py`.
1. Confirm authorization and scope before any scan.
1. Select target input mode:
`-u` for single URL, `-r` for raw request file, `-l` for proxy log, `-m` for bulk targets.
1. Start with low-impact detection first:
prefer `--batch --level=1 --risk=1 --threads=1`.
1. Escalate only when needed:
raise `--level`, `--risk`, or add technique/tamper options after baseline evidence.
1. Run enumeration actions only after injectable parameters are confirmed.
1. Summarize outcomes with:
exact command used, vulnerable parameter(s), DBMS fingerprint, and extraction scope.

## Command Patterns

Use these templates and replace placeholders.
Replace `<sqlmap_cmd>` with user input (or `sqlmap`).

```bash
# Baseline detection
<sqlmap_cmd> -u "https://target.tld/item.php?id=1" --batch --level=1 --risk=1

# Raw request file testing
<sqlmap_cmd> -r "/path/to/request.txt" --batch -p "id"

# DBMS fingerprint + basic enumeration
<sqlmap_cmd> -u "https://target.tld/item.php?id=1" --batch -f --banner --current-db --dbs

# Table dump with explicit scope
<sqlmap_cmd> -u "https://target.tld/item.php?id=1" --batch -D appdb -T users --columns --dump

# Use tamper/proxy when WAF or blocking is suspected
<sqlmap_cmd> -u "https://target.tld/item.php?id=1" --batch --proxy="http://127.0.0.1:8080" --tamper=space2comment
```

## Input Contract

- Required from user: target/scope and authorization confirmation.
- Optional from user: `sqlmap_cmd`.
- Fallback behavior:
use `sqlmap` if `sqlmap_cmd` is not provided.

## Option Mapping

- Need target definition: use one of `-u`, `-r`, `-l`, `-m`, `-d`, `-g`, `-c`.
- Need request shaping: use headers/cookies/auth/proxy/tor/timeouts in `Request`.
- Need higher detection coverage: tune `--level`, `--risk`, `--technique`, `--time-sec`.
- Need schema/data extraction: use `--dbs`, `--tables`, `--columns`, `--dump`, `--search`.
- Need OS or filesystem pivoting: use `--os-cmd`, `--os-shell`, `--file-read`, `--file-write`.
- Need output and repeatability: use `-t`, `--har`, `--output-dir`, `--save`, `-s`.

## Safety Rules

- Require explicit user confirmation of authorization and testing scope.
- Refuse guidance for unauthorized targets or covert misuse.
- Prefer minimally invasive checks first, then escalate deliberately.
- Avoid destructive actions unless user explicitly requests and authorization is clear.
- Redact secrets/tokens from shared logs and command examples.

## References

- Read `references/sqlmap-cheatsheet.md` first for common recipes.
- Read `references/sqlmap-help-hh.txt` for exact flag names and full option groups.
