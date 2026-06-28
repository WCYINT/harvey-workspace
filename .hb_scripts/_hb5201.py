#!/usr/bin/env python3
"""hb#5201 PREPEND script.

Iron rules in force:
- hb#5123: FULL read of HEARTBEAT.md (never f.read(N))
- hb#2589 v2: parse prev_ts from HEARTBEAT.md SoT (not state.json)
- hb#2916: independent regex for silent_streak and cadence
- hb#2550 L1: parts[4]=Capacity, parts[3]=Avail, parts[8]=Mounted
- hb#2874 + hb#3047: rstrip('%') on disk_pct/data_pct to avoid %% doubling
- hb#2842: TZ-aware vs naive datetime (use datetime.now() naive)
- hb#2515: boundary uses local-timedelta (not UTC arithmetic)
- hb#5018: state_delta multi-char fields anchor ';'
- hb#5121: state_delta field regex uses [^;]+ not (\\S+) for group content
- hb#528: atomic write via .tmp + os.replace
- hb#1419: PREPEND via read-existing then concat
- hb#4863: launchagents running order matches existing convention
- hb#2914: silent_streak/cadence_s from HEARTBEAT.md top, not state.json
- hb#5159: launchctl parts[1] exit code (NOT parts[2])
- hb#5178: launchctl total = len(relevant), NOT full line count
- hb#5179: 4-bug stack — disk comma, gw_latency prev from prev header,
          smtp_carry group(2), verdict prev from state_delta group(1)
- hb#5199 REALITY OVERRIDE: trust smtp_health.json, not stale/fake "fresh" claims
"""
import json
import os
import re
import subprocess
import shutil
from datetime import datetime, timedelta

WS = "/Users/fhjtech/.openclaw/workspace"
HB_MD = os.path.join(WS, "HEARTBEAT.md")
STATE_PATH = os.path.join(WS, "memory/heartbeat-state.json")
SMTP_PATH = os.path.join(WS, "memory/smtp_health.json")

# ============================================================
# 1. Capture timestamps FIRST
# ============================================================
now = datetime.now()  # local naive (hb#2842 + hb#2515)
now_str = now.strftime("%Y-%m-%d %H:%M:%S")
print(f"now={now_str}")

# ============================================================
# 2. Read HEARTBEAT.md FULL — source-of-truth (hb#2589 + hb#5123)
# ============================================================
with open(HB_MD) as f:
    existing = f.read()

# Size sanity check (hb#5123)
assert len(existing) >= 5_000, f"HEARTBEAT.md too small ({len(existing)}B), possible read-N bug"
assert existing.startswith('## hb#'), "HEARTBEAT.md structure broken"

m_num = re.match(r"^## hb#(\d+)", existing)
m_ts = re.search(r"^## hb#\d+ \| (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", existing, re.MULTILINE)
m_ss = re.search(r"^## hb#\d+[^\n]*?silent_streak=(\d+)", existing, re.MULTILINE)
m_cad = re.search(r"^## hb#\d+[^\n]*?cadence=~(\d+)s", existing, re.MULTILINE)
m_disk = re.search(r"^## hb#\d+[^\n]*?disk=(\S+)", existing, re.MULTILINE)
m_launch = re.search(r"^## hb#\d+[^\n]*?launchagents=(\S+)", existing, re.MULTILINE)
m_boundary = re.search(r"boundary=([\d.]+)min", existing)
m_smtp = re.search(r"^## hb#\d+[^\n]*?smtp=(\S+)", existing, re.MULTILINE)
m_state_delta = re.search(r"^state_delta: (.+)$", existing, re.MULTILINE)
m_mode = re.search(r"^## hb#\d+[^\n]*?zone=(\S+)", existing, re.MULTILINE)
# hb#5179: prev_gw_latency from prev header (e.g., gw=200@3ms,...)
m_prev_gw_lat = re.search(r"^## hb#\d+[^\n]*?gw=\d+@(\d+)ms", existing, re.MULTILINE)

assert m_num and m_ts and m_ss and m_cad, "HEARTBEAT.md top parse failed"

prev_hb_num = int(m_num.group(1))
prev_ts_str = m_ts.group(1)
prev_silent_streak = int(m_ss.group(1))
prev_cadence_s = int(m_cad.group(1))
prev_disk = m_disk.group(1) if m_disk else "?"
prev_launchagents = m_launch.group(1) if m_launch else "?"
prev_boundary_min = float(m_boundary.group(1)) if m_boundary else 0.0
prev_smtp = m_smtp.group(1) if m_smtp else "?"
prev_state_delta = m_state_delta.group(1) if m_state_delta else ""
prev_mode = m_mode.group(1) if m_mode else "?"
prev_gw_latency_ms_hdr = int(m_prev_gw_lat.group(1)) if m_prev_gw_lat else 0

prev_dt = datetime.strptime(prev_ts_str, "%Y-%m-%d %H:%M:%S")
elapsed_s = int((now - prev_dt).total_seconds())
new_hb_num = prev_hb_num + 1
new_silent_streak = prev_silent_streak + 1
new_cadence_s = elapsed_s  # actual measured cadence
print(f"prev_hb_num={prev_hb_num} prev_ts={prev_ts_str} prev_ss={prev_silent_streak} prev_cad={prev_cadence_s}s elapsed={elapsed_s}s")
print(f"new_hb_num={new_hb_num} new_ss={new_silent_streak} new_cad={new_cadence_s}s")
print(f"prev_gw_latency_ms (from prev header) = {prev_gw_latency_ms_hdr}")

# ============================================================
# 3. Health checks
# ============================================================
# Gateway — probe multiple endpoints (hb#5199 mentioned 18789/18790/18791/18792)
gw_ports = [18789, 18790, 18791, 18792]
gw_results = []
for port in gw_ports:
    try:
        r = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}|%{time_total}", f"http://127.0.0.1:{port}/healthz"],
            capture_output=True, text=True, timeout=5
        )
        out = r.stdout.split("|")
        code = out[0] if len(out) > 0 else "?"
        t = out[1] if len(out) > 1 else "?"
        lat_ms = int(float(t) * 1000) if t not in ("?", "") else 0
    except Exception as e:
        code, lat_ms = "000", 0
    gw_results.append(f"{code}@{lat_ms}ms")

gw_str = ",".join(gw_results)
gw_first_code = gw_results[0].split("@")[0]
gw_first_lat = int(gw_results[0].split("@")[1].rstrip("ms"))
print(f"gateway: {gw_str} (first: {gw_first_code}@{gw_first_lat}ms)")

# Count OK probes
gw_ok_count = sum(1 for r in gw_results if r.startswith("200@"))
gw_fail_count = sum(1 for r in gw_results if not r.startswith("200@"))

# SMTP — read from smtp_health.json (REALITY OVERRIDE — trust actual JSON, not stale claims)
with open(SMTP_PATH) as f:
    smtp_hist = json.load(f)
last_smtp = smtp_hist[-1] if smtp_hist else {}
smtp_ts_str = last_smtp.get("timestamp", "")
# Strip TZ (hb#2842)
if "+" in smtp_ts_str or smtp_ts_str.endswith("Z"):
    smtp_ts_str = smtp_ts_str.split("+")[0].rstrip("Z")
smtp_dt = datetime.fromisoformat(smtp_ts_str)
smtp_age_min = max(0, int((now - smtp_dt).total_seconds() / 60))
smtp_lat_ms = last_smtp.get("latency_ms", 0)
smtp_healthy = last_smtp.get("healthy", False)
smtp_status_str = "HEALTH" if smtp_healthy else "FAIL"

# Try fresh probe — if env not set, this will fail silently
smtp_fresh_probe_done = False
auth = os.environ.get("HARVEY_EMAIL_AUTH", "")
if auth:
    try:
        r = subprocess.run(
            ["python3", "-c", f"""
import smtplib, time
try:
    s = smtplib.SMTP_SSL('smtp.163.com', 465, timeout=10)
    t0 = time.time()
    s.login('wcyint@163.com', '{auth}')
    lat = int((time.time()-t0)*1000)
    s.quit()
    print(f'OK|{{lat}}')
except Exception as e:
    print(f'FAIL|{{e}}')
"""], capture_output=True, text=True, timeout=15
        )
        out = r.stdout.strip()
        if out.startswith("OK|"):
            smtp_fresh_probe_done = True
            smtp_lat_ms = int(out.split("|")[1])
            smtp_healthy = True
            smtp_status_str = "HEALTH"
            # Append to smtp_health.json
            smtp_hist.append({
                "timestamp": now.isoformat(),
                "healthy": True,
                "latency_ms": smtp_lat_ms,
                "probe": "EHLO"
            })
            with open(SMTP_PATH + ".tmp", "w") as f:
                json.dump(smtp_hist, f, indent=2, ensure_ascii=False)
            os.replace(SMTP_PATH + ".tmp", SMTP_PATH)
            smtp_age_min = 0
    except Exception as e:
        pass

smtp_carry_str = "false" if smtp_fresh_probe_done else "true"
smtp_str = f"{smtp_status_str}({smtp_age_min}m,{smtp_lat_ms}ms,carry={smtp_carry_str})"
print(f"smtp: {smtp_str} (fresh_probe={smtp_fresh_probe_done})")

# LaunchAgents (hb#5159: parts[1] for exit code; hb#5178: total=len(relevant))
r = subprocess.run(["launchctl", "list"], capture_output=True, text=True, timeout=10)
relevant = []
for line in r.stdout.splitlines():
    parts = line.split()
    if len(parts) < 3:
        continue
    label = parts[2] if len(parts) >= 3 else ""
    if any(k in label.lower() for k in ['hjtech', 'openclaw', 'harvey', 'hermes']):
        relevant.append(line)

nz_hj = []
running = 0
nonzero = 0
for line in relevant:
    parts = line.split()
    if len(parts) < 3:
        continue
    pid_str = parts[0]
    exit_code = parts[1]  # ALWAYS parts[1] (hb#5159)
    label = parts[2]
    is_running = pid_str not in ("-", "")
    if is_running:
        try:
            pid = int(pid_str)
            nz_hj.append(f"{label}(pid={pid},exit={exit_code})")
            if pid > 0:
                running += 1
            if exit_code != "0":
                nonzero += 1
        except ValueError:
            pass

total = len(relevant)  # hb#5178: MUST be len(relevant), not full line count
assert total < 100, f"launchctl total too large ({total}), likely unfiltered"
launchagents_str = f"{nonzero}/{total}/{running}"
print(f"launchagents: {launchagents_str} (nz: {', '.join(nz_hj[:5])})")

# Disk (hb#2550 L1 + hb#2874 + hb#3047 + hb#5179 disk comma)
# Use df -h (no arg) to get all filesystems including /System/Volumes/Data
r = subprocess.run(["df", "-h"], capture_output=True, text=True, timeout=10)
lines = r.stdout.strip().splitlines()
disk_pct = "?"
disk_avail = "?"
data_pct = "?"
data_avail = "?"
print(f"df -h returned {len(lines)} lines")
for ln in lines[1:]:
    parts = ln.split()
    if len(parts) < 9:
        continue
    # macOS sometimes splits "Mounted on" across 2 cols when path is long.
    # If len==9, parts[8] is the mount. If len==10, parts[8]='Mounted', parts[9]='on'.
    if len(parts) == 10 and parts[8] == 'Mounted' and parts[9] == 'on':
        continue  # header line artifact (shouldn't happen but defensive)
    mount = parts[8] if len(parts) == 9 else (parts[8] + ' ' + parts[9])
    if mount == '/':
        disk_pct = parts[4]
        disk_avail = parts[3]
    elif mount == '/System/Volumes/Data':
        data_pct = parts[4]
        data_avail = parts[3]

# Fallback: if data_pct still missing, run separate df for /System/Volumes/Data
if data_pct == "?":
    r2 = subprocess.run(["df", "-h", "/System/Volumes/Data"], capture_output=True, text=True, timeout=10)
    for ln in r2.stdout.strip().splitlines()[1:]:
        parts = ln.split()
        if len(parts) >= 9 and 'Data' in parts[8]:
            data_pct = parts[4]
            data_avail = parts[3]
            break

print(f"disk_pct={disk_pct}, disk_avail={disk_avail}, data_pct={data_pct}, data_avail={data_avail}")

disk_pct_n = disk_pct.rstrip('%') if disk_pct.endswith('%') else disk_pct
data_pct_n = data_pct.rstrip('%') if data_pct.endswith('%') else data_pct
# hb#5179: must have comma after '/'  →  disk=N%(/,Navail)
disk_str = f"disk={disk_pct_n}%(/,{disk_avail}) {data_pct_n}%(Data,{data_avail})"
assert '%%' not in disk_str and '/,' in disk_str, f"disk format bug: {disk_str}"
assert data_pct != "?", f"data_pct missing! lines:\n{r.stdout}"
print(f"{disk_str}")

# Mode (hb#2510 L1)
hour = now.hour
mode_str = "NIGHT-MODE-4x🌙" if (hour >= 23 or hour < 8) else ("EVE-MODE-2x" if hour >= 18 else "DAY-MODE-1x☀️")
print(f"mode: {mode_str} (hour={hour})")

# Boundary (hb#2510 L1 + hb#2515)
yesterday_2300 = (now - timedelta(days=1)).replace(hour=23, minute=0, second=0, microsecond=0)
boundary_min = round((now - yesterday_2300).total_seconds() / 60, 2)
assert 0 < boundary_min < 24*60, f"boundary_min out of range: {boundary_min}"
print(f"boundary: {boundary_min}min")

# ============================================================
# 4. Verdict (hb#5018 — gw_only, 3+ fails = FAIL)
# ============================================================
if gw_fail_count >= 3:
    verdict = "FAIL"
elif gw_fail_count > 0 or gw_first_lat > 500 or smtp_age_min > 240:
    verdict = "DEGRADED"
else:
    verdict = "OK"
print(f"verdict: {verdict} (gw_ok={gw_ok_count}/4, gw_first_lat={gw_first_lat}ms, smtp_age={smtp_age_min}m)")

# ============================================================
# 5. Build new entry
# ============================================================
header = (
    f"## hb#{new_hb_num} | {now_str} | "
    f"silent_streak={new_silent_streak} cadence=~{new_cadence_s}s "
    f"gw={gw_str} smtp={smtp_str} zone={mode_str.split('-')[0]} "
    f"launchagents={launchagents_str} {disk_str} boundary={boundary_min}min"
)

# state_delta — hb#5179 group(1)=OLD, group(2)=CURRENT (prev's CURRENT is what's in prev_state_delta)
prev_sd = prev_state_delta
def parse_prev(pattern):
    m = re.search(pattern, prev_sd)
    return m.group(2) if m else "?"

# hb#5179: verdict_prev = group(1) (the OLD value, not CURRENT)
def parse_prev_old(pattern):
    m = re.search(pattern, prev_sd)
    return m.group(1) if m else "OK"

prev_ss_v = parse_prev(r"silent_streak:([^;]+)->([^;]+?);")
prev_cad_v = parse_prev(r"cadence_s:([^;]+)->([^;]+?);")
prev_bd_v = parse_prev(r"boundary_min:([^;]+)->([^;]+?);")
prev_gw_lat_v = parse_prev(r"gw_latency_ms:([^;]+)->([^;]+?);")
prev_smtp_age_v = parse_prev(r"smtp_age_min:([^;]+)->([^;]+?);")
prev_smtp_lat_v = parse_prev(r"smtp_latency_ms:([^;]+)->([^;]+?);")
prev_smtp_status_v = parse_prev(r"smtp_status:([^;]+)->([^;]+?);")
prev_smtp_carry_v = parse_prev(r"smtp_carry:([^;]+)->([^;]+?);")  # hb#5179: group(2) is CURRENT
prev_launchagents_v = parse_prev(r"launchagents:([^;]+)->([^;]+?);")
prev_mode_v = parse_prev(r"mode:([^;]+)->([^;]+?);")
prev_disk_v_match = re.search(r"disk:([^;]+);", prev_sd)
prev_disk_v = "?"
if prev_disk_v_match:
    disk_field = prev_disk_v_match.group(1)  # e.g. "OLD->NEW" or just "VALUE"
    if "->" in disk_field:
        # Take the LAST part (the CURRENT/NEW from prev entry)
        prev_disk_v = disk_field.rsplit("->", 1)[1]
    else:
        prev_disk_v = disk_field
# hb#5179: verdict_prev = group(1) (OLD)
prev_verdict_v = parse_prev_old(r"verdict:([^;]+)->([^;]+?);")

state_delta = (
    f"silent_streak:{prev_ss_v}->{new_silent_streak};"
    f"cadence_s:{prev_cad_v}->{new_cadence_s};"
    f"boundary_min:{prev_bd_v}->{boundary_min};"
    f"gw_latency_ms:{prev_gw_lat_v}->{gw_first_lat};"
    f"smtp_age_min:{prev_smtp_age_v}->{smtp_age_min};"
    f"smtp_latency_ms:{prev_smtp_lat_v}->{smtp_lat_ms};"
    f"smtp_status:{prev_smtp_status_v}->{smtp_status_str};"
    f"verdict:{prev_verdict_v}->{verdict};"
    f"launchagents:{prev_launchagents_v}->{launchagents_str};"
    f"mode:{prev_mode_v}->{mode_str};"
    f"smtp_carry:{prev_smtp_carry_v}->{smtp_carry_str};"
    f"disk:{prev_disk_v}->{disk_pct_n}%(/,{disk_avail}) {data_pct_n}%(Data,{data_avail})"
)
# hb#5121 verify
assert '%%' not in state_delta, f"state_delta has %% doubling: {state_delta}"
assert not re.search(r"launchagents:[^;]*true[^;]*;", state_delta), f"launchagents bled 'true'"
assert not re.search(r"mode:[^;]*true[^;]*;", state_delta), f"mode bled 'true'"
assert '/,' in state_delta, f"disk missing comma after /: {state_delta}"

# Bullet — sub-poll format
nz_summary = ", ".join(nz_hj[:5]) if nz_hj else "(none)"
boundary_text = f"T+{int(boundary_min//60)}h{int(boundary_min%60)}m past 23:00 boundary"
ordinal = f"{new_silent_streak}th consecutive"
bullet = (
    f"- heartbeat self-check #{new_silent_streak} (hb#{new_hb_num}) @ {now_str} | "
    f"cron-event:heartbeat-poll | elapsed: {elapsed_s}s | "
    f"cadence={elapsed_s}s (prev={prev_cadence_s}s) | "
    f"silent_streak={new_silent_streak} ({ordinal}) | "
    f"zone={mode_str.split('-')[0]} mode={mode_str} | "
    f"gw: {gw_str} [{verdict}] | smtp: {smtp_str}"
)

new_entry = f"{header}\nstate_delta: {state_delta}\n{bullet}\n"

# ============================================================
# 6. Backup before PREPEND (hb#5123)
# ============================================================
backup_path = f"{HB_MD}.pre_hb{new_hb_num}"
shutil.copy2(HB_MD, backup_path)
print(f"backup: {backup_path}")

# ============================================================
# 7. PREPEND + atomic write (hb#528 + hb#1419)
# ============================================================
new_content = new_entry + existing
tmp = HB_MD + ".tmp"
with open(tmp, "w") as f:
    f.write(new_content)
os.replace(tmp, HB_MD)

# Post-write verify
size_after = os.path.getsize(HB_MD)
assert size_after > len(existing), f"POST-WRITE: shrunk! {len(existing)} -> {size_after}"
print(f"OK: HEARTBEAT.md grew {len(existing)} -> {size_after} bytes (+{size_after - len(existing)})")

# ============================================================
# 8. Update state.json atomically (hb#528)
# ============================================================
with open(STATE_PATH) as f:
    state = json.load(f)
state["last_hb_id"] = f"hb#{new_hb_num}"
state["hb_count"] = new_hb_num
state["silent_streak"] = new_silent_streak
state["consecutive_ok"] = (state.get("consecutive_ok", 0) + 1) if verdict == "OK" else 0
state["cadence_s"] = new_cadence_s
state["prev_cadence_s"] = prev_cadence_s
state["last_cadence_s"] = new_cadence_s
state["boundary_min"] = boundary_min
state["last_boundary_min"] = prev_boundary_min
state["gw_latency_ms"] = gw_first_lat
state["last_gw_latency_ms"] = gw_first_lat
state["smtp_age_min"] = smtp_age_min
state["smtp_latency_ms"] = smtp_lat_ms
state["smtp_status"] = smtp_status_str
state["last_smtp_age_min"] = smtp_age_min
state["last_smtp_latency_ms"] = smtp_lat_ms
state["smtp"] = smtp_str
state["last_smtp"] = smtp_str
state["last_smtp_status"] = smtp_status_str
state["last_smtp_carry"] = smtp_carry_str
state["smtp_carry"] = smtp_carry_str == "true"
state["verdict"] = verdict
state["last_verdict"] = prev_verdict_v
state["verdict_chain"] = f"{prev_verdict_v}->{verdict}"
state["launchagents"] = launchagents_str
state["last_launchagents"] = prev_launchagents
state["launchd_count"] = total
state["launchd_total"] = total
state["launchd_nz"] = nonzero
state["launchd_running"] = running
state["launchagents_nonzero"] = nonzero
state["launchagents_running"] = running
state["launchagents_total"] = total
state["launchagents_nz"] = nonzero
state["launchd_nz_names"] = nz_hj
state["launchagents_nz_names"] = nz_hj
state["last_launchagents_nz_names"] = nz_hj
state["last_launchd_nz_names"] = nz_hj
state["mode"] = mode_str
state["last_mode"] = prev_mode
state["disk"] = f"{disk_pct_n}%(/,{disk_avail}) {data_pct_n}%(Data,{data_avail})"
state["last_disk"] = prev_disk
state["updated_at"] = now_str
state["state_delta"] = state_delta

tmp = STATE_PATH + ".tmp"
with open(tmp, "w") as f:
    json.dump(state, f, indent=2, ensure_ascii=False)
os.replace(tmp, STATE_PATH)
print(f"OK: state.json updated")

print("DONE")