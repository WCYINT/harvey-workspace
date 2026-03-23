---
name: debug
version: "3.2.0"
author: BytesAgain
homepage: https://bytesagain.com
source: https://github.com/bytesagain/ai-skills
tags: [debug, error, trace, log, crash, stacktrace]
description: "Trace errors in logs, parse stack traces, detect memory leaks, profile commands, and debug HTTP."
---

# Debug

Trace errors in log files, parse stack traces, detect memory leaks, profile slow code paths.

## Commands

### trace
Find error patterns in log files.
```bash
bash scripts/script.sh trace /var/log/app.log
bash scripts/script.sh trace --pattern "OOM\|Segfault\|FATAL" /var/log/syslog
bash scripts/script.sh trace --last 1h /var/log/app.log
```

### stacktrace
Parse and summarize a stack trace or crash dump.
```bash
bash scripts/script.sh stacktrace crash.log
echo "TypeError: cannot read property 'x' of undefined\n    at foo (app.js:42)" | bash scripts/script.sh stacktrace -
```

### leaks
Detect potential memory leaks by analyzing process memory over time.
```bash
bash scripts/script.sh leaks --pid 1234
bash scripts/script.sh leaks --pid 1234 --duration 60 --interval 5
```

### profile
Measure execution time of a command, show CPU and memory usage.
```bash
bash scripts/script.sh profile "python3 slow_script.py"
bash scripts/script.sh profile --repeat 5 "curl -s https://api.example.com"
```

### diff-logs
Compare two log files and highlight differences (new errors, missing entries).
```bash
bash scripts/script.sh diff-logs before.log after.log
bash scripts/script.sh diff-logs --errors-only old.log new.log
```

### http
Debug HTTP requests — show headers, timing, redirects, SSL info.
```bash
bash scripts/script.sh http https://example.com
bash scripts/script.sh http --verbose --timing https://api.example.com/health
```

## Output
- Plain text summary to stdout
- Error counts, unique patterns, timestamps
- Exit code 0 = clean, 1 = errors found


## Requirements
- bash 4+
- python3 (standard library only)

## Feedback
https://bytesagain.com/feedback/
Powered by BytesAgain | bytesagain.com
