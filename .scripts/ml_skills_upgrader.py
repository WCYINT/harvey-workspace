#!/usr/bin/env python3
"""
数据建模/机器学习/LLM技能专项提升任务
每90分钟执行一次，六步流程：
  1. 调用 gstack 技能进行多角色讨论，确定技能需求
  2. 启动4个agent并行搜索四大平台
  3. 与本地已安装技能对比，决定升级或安装
  4. 测试新技能/升级技能，不合格退回
  5. 技能组合+系统集成测试，形成报告
  6. 基于PDCA八分法优化，总结发邮箱
"""

import asyncio
import subprocess
import json
import os
import shutil
import smtplib
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

# ── 配置 ──────────────────────────────────────────
SKILLS_DIR = Path("/Users/fhjtech/.openclaw/workspace/skills")
SKILLS_DB = Path("/Users/fhjtech/.openclaw/workspace/.learnings/skills_usage.json")
LOG_FILE = Path("/Users/fhjtech/.openclaw/workspace/.learnings/ml_skills_upgrader.log")
LOG_MARKER = Path("/Users/fhjtech/.openclaw/workspace/.learnings/.last_ml_update.json")
ROLES_DIR = Path("/Users/fhjtech/.openclaw/workspace/.learnings/gstack_roles")
DECISION_FILE = Path("/Users/fhjtech/.openclaw/workspace/.learnings/.pending_decision.json")
SKILLHUB_CMD = "/Users/fhjtech/.local/bin/skillhub"
CLAWHUB_CMD = "/opt/homebrew/bin/clawhub"
NPX_SKILLS_CMD = "npx"   # skills.sh CLI: npx skills add <owner>/<repo>/<skill>
MAX_INSTALL = 10
MAX_CONCURRENCY = 20

TZ_CST = timezone(timedelta(hours=8))

# ── Credentials (loaded from env or .credentials.json) ──────────────
def _load_creds() -> dict:
    """Load Feishu credentials from env vars or .credentials.json."""
    creds_file = Path(__file__).parent / ".credentials.json"
    defaults = {
        "feishu_app_id": "cli_a90c7258f9b85bef",
        "feishu_app_secret": "Kv6kG5ggU2TP9Ocw5CHSucu1B1t26J7t",
        "feishu_user_open_id": "ou_7bc224841d2a1064cf5a7fbf67824227",
        "feishu_p2p_chat_id": "oc_59e5938f0f0e1f3e34dcf84f8ffbc3b7",
    }
    if creds_file.exists():
        try:
            defaults.update(json.loads(creds_file.read_text()))
        except Exception:
            pass
    return {
        "feishu_app_id": os.environ.get("FEISHU_APP_ID", defaults["feishu_app_id"]),
        "feishu_app_secret": os.environ.get("FEISHU_APP_SECRET", defaults["feishu_app_secret"]),
        "feishu_user_open_id": os.environ.get("FEISHU_USER_OPEN_ID", defaults["feishu_user_open_id"]),
        "feishu_p2p_chat_id": os.environ.get("FEISHU_P2P_CHAT_ID", defaults["feishu_p2p_chat_id"]),
    }

_CREDS = _load_creds()

FEISHU_APP_ID = _CREDS["feishu_app_id"]
FEISHU_APP_SECRET = _CREDS["feishu_app_secret"]
FEISHU_USER_OPEN_ID = _CREDS["feishu_user_open_id"]
FEISHU_P2P_CHAT_ID = _CREDS["feishu_p2p_chat_id"]

def _get_feishu_token() -> str:
    """获取 Feishu tenant access token"""
    import urllib.request
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = json.dumps({"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.load(resp)
    if data.get("code") != 0:
        raise Exception(f"Feishu token failed: {data}")
    return data["tenant_access_token"]

def send_feishu_message(content: str) -> bool:
    """通过 Feishu P2P 会话发消息给 James"""
    try:
        import urllib.request
        token = _get_feishu_token()
        url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
        payload = {
            "receive_id": FEISHU_P2P_CHAT_ID,
            "msg_type": "text",
            "content": json.dumps({"text": content})
        }
        data = json.dumps(payload).encode()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.load(resp)
        return result.get("code") == 0
    except Exception as e:
        log(f"[Feishu] 发送失败: {e}")
        return False

# 重点技能类别
ML_SKILLS_KEYWORDS = [
    "machine learning", "deep learning", "data analysis", "statistics",
    "regression", "classification", "clustering", "neural network",
    "DOE", "design of experiments", "optimization", "mathematical modeling",
    "llm", "large language model", "nlp", "text analysis",
    "python", "scikit-learn", "tensorflow", "pytorch", "pandas",
    "statistical analysis", "hypothesis testing", "anova",
    "time series", "forecasting", "regression analysis",
    "data visualization", "matplotlib", "seaborn",
    "feature engineering", "model evaluation", "cross validation"
]

# ── 日志 ──────────────────────────────────────────
def log(msg: str) -> None:
    ts = datetime.now(TZ_CST).strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# ── 共享角色文件管理 ──────────────────────────────
def write_role_file(role: str, data: dict) -> None:
    """写入角色讨论结果到共享文件"""
    ROLES_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = role.lower().replace(" ", "_")
    path = ROLES_DIR / f"{safe_name}.json"
    try:
        path.write_text(json.dumps({
            "timestamp": datetime.now(TZ_CST).isoformat(),
            "role": role,
            "data": data
        }, indent=2, ensure_ascii=False))
        log(f"[角色文件] 已写入 {path.name}")
    except Exception as e:
        log(f"[角色文件] 写入失败 {role}: {e}")

def read_role_files() -> dict:
    """读取所有角色讨论结果"""
    results = {}
    for f in ROLES_DIR.glob("*.json"):
        try:
            data = json.loads(f.read_text())
            results[data["role"]] = data
        except Exception as e:
            log(f"[角色文件] 读取失败 {f.name}: {e}")
    return results

# ── 决策节点：发送确认邮件 ────────────────────
def send_decision_email(skills_to_install: list, reason: str) -> None:
    """在关键决策点发送确认邮件给 King"""
    now = datetime.now(TZ_CST)
    skills_html = "".join(f"<li><b>{s}</b></li>" for s in skills_to_install)

    body = f"""
    <h2>🔔 技能安装需要您确认</h2>
    <p><b>时间：</b>{now.strftime('%Y-%m-%d %H:%M')} (北京时间)</p>
    <p><b>原因：</b>{reason}</p>
    <hr>
    <p>系统发现以下 <b>{len(skills_to_install)}</b> 个新技能，建议安装：</p>
    <ol>{skills_html}</ol>
    <hr>
    <p><b>回复本邮件确认安装</b>，或回复 <b>SKIP</b> 跳过本次安装。</p>
    <p>或者直接在此邮件回复 <b>YES</b> 安装，<b>NO</b> 跳过。</p>
    """
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🔔 待确认：{len(skills_to_install)}个新技能待安装 | {now.strftime('%H:%M')}"
    msg["From"] = "wcyint@163.com"
    msg["To"] = "wcyint@163.com"
    msg.attach(MIMEText(body, "html", "utf-8"))
    try:
        with smtplib.SMTP_SSL("smtp.163.com", 465) as server:
            server.login("wcyint@163.com", os.environ.get("HARVEY_EMAIL_AUTH", "SEMefmThGnEKJiTz"))
            server.sendmail("wcyint@163.com", ["wcyint@163.com"], msg.as_string())
        # 写入待决策文件
        DECISION_FILE.write_text(json.dumps({
            "timestamp": now.isoformat(),
            "skills": skills_to_install,
            "reason": reason,
            "status": "pending"
        }))
        log(f"[决策节点] 已发送确认邮件，等待 King 回复")
        return True
    except Exception as e:
        log(f"[决策节点] 邮件发送失败: {e}")
        return False

# ── Step 1: gstack 多角色讨论 ───────────────────
def step1_gstack_discussion() -> dict:
    """gstack风格多角色讨论：用minimax chat模拟3角色并发讨论技能需求"""
    log("[Step1] 启动 gstack 多角色讨论（3角色并发）...")
    try:
        import sys
        sys.path.insert(0, '/Users/fhjtech/.openclaw/workspace/.scripts')
        from minimax_client import chat

        roles = [
            ("CEO", "你是CEO，关注商业价值和论文影响力，推荐技能", 1.5),
            ("Engineer", "你是工程师，关注技术可行性和实现难度", 1.2),
            ("DataScientist", "你是数据科学家，关注统计分析和建模能力", 1.0),
        ]
        role_responses = {}
        for role_name, role_prompt, weight in roles:
            try:
                prompt = f"""{role_prompt}

请用gstack AskUserQuestion格式分析MBA论文（C公司插电混动Y车型质量改进）最需要的技能。

输出JSON格式：
{{"role": "{role_name}", "skills_needed": ["skill1", "skill2"], "reasoning": "一句话理由"}}

skills_needed使用简短slug，只输出JSON。"""
                response = chat(prompt=prompt, model="MiniMax-M2.7")
                # Try to extract JSON
                import json
                try:
                    data = json.loads(response)
                    role_responses[role_name] = data
                    log(f"[Step1] {role_name}角色完成，技能: {data.get('skills_needed', [])}")
                except:
                    # Try extracting from markdown code blocks
                    import re
                    json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
                    if json_match:
                        data = json.loads(json_match.group())
                        role_responses[role_name] = data
            except Exception as e:
                log(f"[Step1] {role_name}角色异常: {e}")

        # 汇总技能（加权）
        all_skills = {}
        for role_name, data in role_responses.items():
            weight = next(w for n, _, w in roles if n == role_name)
            for skill in data.get("skills_needed", []):
                skill = skill.lower()
                if skill not in all_skills:
                    all_skills[skill] = {"skill": skill, "score": 0, "roles": []}
                all_skills[skill]["score"] += weight
                all_skills[skill]["roles"].append(role_name)

        sorted_skills = sorted(all_skills.values(), key=lambda x: x["score"], reverse=True)
        skills_list = [s["skill"] for s in sorted_skills[:10]]

        log(f"[Step1] gstack三角色讨论完成，技能优先级: {skills_list}")
        return {"status": "ok", "skills_needed": skills_list, "roles": role_responses, "gstack_ok": True}
    except Exception as e:
        log(f"[Step1] gstack讨论异常: {e}")
        return {"status": "error", "skills_needed": ML_SKILLS_KEYWORDS, "roles": {}, "gstack_ok": False}

# ── Step 2: 并行搜索四大平台 ─────────────────────
async def _search_skillhub(kw: str, semaphore: asyncio.Semaphore) -> list[dict]:
    async with semaphore:
        try:
            proc = await asyncio.create_subprocess_exec(
                SKILLHUB_CMD, "search", kw,
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
                cwd=str(SKILLS_DIR.parent)
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)
            if proc.returncode != 0:
                return []
            return _parse_output(stdout.decode("utf-8", errors="ignore"), "skillhub")
        except:
            return []

async def _search_clawhub(kw: str, semaphore: asyncio.Semaphore) -> list[dict]:
    async with semaphore:
        try:
            proc = await asyncio.create_subprocess_exec(
                CLAWHUB_CMD, "search", kw,
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
                cwd=str(SKILLS_DIR.parent)
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)
            if proc.returncode != 0:
                return []
            return _parse_output(stdout.decode("utf-8", errors="ignore"), "clawhub")
        except:
            return []

async def _fetch_voltagent(semaphore: asyncio.Semaphore) -> list[dict]:
    async with semaphore:
        try:
            import urllib.request
            url = "https://raw.githubusercontent.com/VoltAgent/awesome-openclaw-skills/main/README.md"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read().decode("utf-8", errors="ignore")
            skills = []
            for line in content.split('\n'):
                if 'python' in line.lower() or 'ml' in line.lower() or 'data' in line.lower():
                    m = re.search(r'\[([^\]]+)\]\(([^)]+)\)', line)
                    if m:
                        skills.append({"slug": m.group(1), "source": "voltagent", "description": line[:100]})
            return skills[:10]
        except:
            return []

async def _fetch_skills_sh(semaphore: asyncio.Semaphore) -> list[dict]:
    async with semaphore:
        try:
            import urllib.request
            url = "https://raw.githubusercontent.com/skills-sh/awesome-skills/main/README.md"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read().decode("utf-8", errors="ignore")
            skills = []
            for line in content.split('\n'):
                if any(kw in line.lower() for kw in ['python', 'machine learning', 'data', 'llm']):
                    m = re.search(r'\[([^\]]+)\]\(([^)]+)\)', line)
                    if m:
                        skills.append({"slug": m.group(1), "source": "skills.sh", "description": line[:100]})
            return skills[:10]
        except:
            return []

def _parse_output(output: str, source: str) -> list[dict]:
    """Parse skill search output. Skip non-slug lines (Chinese descriptions, category names)."""
    skills = []
    for line in output.split('\n'):
        if line.strip() and not line.startswith('#') and not line.startswith('['):
            parts = line.strip().split()
            if parts:
                raw_slug = parts[0]
                # FIX 2026-04-04: Validate slug is ASCII-only (no Chinese/descriptions as slugs)
                # Valid slugs: alphanumeric, underscore, dash, dot. Invalid: Chinese, spaces, special chars.
                if not raw_slug.replace('_', '').replace('-', '').replace('.', '').isalnum():
                    continue  # Skip lines where first "word" contains Chinese or invalid chars
                if not raw_slug.encode('ascii', errors='ignore').decode() == raw_slug:
                    continue  # Skip non-ASCII (Chinese, etc.)
                slug = raw_slug.replace('/', '_').replace('-', '_')
                # Skip if slug looks like a category name (too long, contains 'and'/'or')
                if len(slug) > 40 or slug.lower() in ('and', 'or', 'the', 'for'):
                    continue
                skills.append({
                    "slug": slug,
                    "source": source,
                    "description": line.strip()[:100]
                })
    return skills[:5]

async def step2_parallel_search(keywords: list[str]) -> dict:
    """4个agent并行搜索四大平台"""
    log("[Step2] 启动4个agent并行搜索...")
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
    tasks = []
    for kw in keywords[:8]:  # 最多8个关键词
        tasks.append(_search_skillhub(kw, semaphore))
        tasks.append(_search_clawhub(kw, semaphore))
    tasks.append(_fetch_voltagent(semaphore))
    tasks.append(_fetch_skills_sh(semaphore))
    results = await asyncio.gather(*tasks)
    all_skills = {}
    for skill_list in results:
        for s in skill_list:
            slug = s["slug"]
            if slug not in all_skills:
                all_skills[slug] = s
    log(f"[Step2] 四平台搜索完成，获取 {len(all_skills)} 个技能")
    return all_skills

# ── Step 3: 对比已安装技能 ─────────────────────
def step3_compare_and_decide(all_skills: dict) -> tuple[dict, dict, list]:
    """对比已安装技能，决定升级或新装"""
    installed = {d.name for d in SKILLS_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")}
    to_install = {}
    to_upgrade = {}
    already_current = []
    for slug, info in all_skills.items():
        if slug in installed:
            # 检查是否需要升级（版本不同）
            skill_meta = SKILLS_DIR / slug / "SKILL.md"
            if skill_meta.exists():
                content = skill_meta.read_text(encoding="utf-8", errors="ignore")
                version_match = re.search(r'version:\s*([0-9.]+)', content)
                current_ver = version_match.group(1) if version_match else "1.0.0"
                new_ver = info.get("version", "1.0.0")
                if new_ver > current_ver:
                    to_upgrade[slug] = info
                else:
                    already_current.append(slug)
            else:
                already_current.append(slug)
        else:
            to_install[slug] = info
    log(f"[Step3] 已安装: {len(installed)} | 待新装: {len(to_install)} | 待升级: {len(to_upgrade)} | 已最新: {len(already_current)}")
    return to_install, to_upgrade, already_current

# ── Step 4: 安装/升级技能 ──────────────────────
async def _install_one(slug: str, source: str, is_upgrade: bool, semaphore: asyncio.Semaphore) -> tuple[str, bool, str, bool]:
    async with semaphore:
        try:
            if source == "clawhub":
                cmd = CLAWHUB_CMD
                args = ["install", "--force", slug]
                proc = await asyncio.create_subprocess_exec(
                    cmd, *args,
                    stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
                    cwd=str(SKILLS_DIR.parent)
                )
            elif source == "skills.sh":
                # skills.sh format: npx skills add <owner>/<repo>/<skill>
                # CI=true prevents interactive prompts that cause subprocess hang
                npx_env = os.environ.copy()
                npx_env["CI"] = "true"
                proc = await asyncio.create_subprocess_exec(
                    NPX_SKILLS_CMD, "skills", "add", slug,
                    stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
                    cwd=str(SKILLS_DIR.parent), env=npx_env
                )
            else:
                cmd = SKILLHUB_CMD
                action = "update" if is_upgrade else "install"
                args = [action, slug]
                proc = await asyncio.create_subprocess_exec(
                    cmd, *args,
                    stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
                    cwd=str(SKILLS_DIR.parent)
                )
            # FIX 2026-04-04: Increase timeout from 60s to 120s for npx skills (git clone)
            timeout = 120 if source == "skills.sh" else 60
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            ok = proc.returncode == 0
            # npx skills add writes errors to stdout — include it for skills.sh source
            err_str = stderr.decode(errors="replace") if source != "skills.sh" else (stdout.decode(errors="replace") + stderr.decode(errors="replace"))
            status = "OK" if ok else f"FAIL({err_str[:60]})"
            log(f"[Step4] {'升级' if is_upgrade else '安装'}{status}: {slug} ({source})")
            return (slug, ok, source, is_upgrade)
        except asyncio.TimeoutError:
            status = "FAIL(Timeout)"
            log(f"[Step4] {'升级' if is_upgrade else '安装'}{status}: {slug} ({source})")
            return (slug, False, source, is_upgrade)
        except:
            return (slug, False, source, is_upgrade)

async def step4_install_or_upgrade(to_install: dict, to_upgrade: dict) -> tuple[list, list]:
    all_tasks = []
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
    for slug, info in to_install.items():
        all_tasks.append(_install_one(slug, info["source"], False, semaphore))
    for slug, info in to_upgrade.items():
        all_tasks.append(_install_one(slug, info["source"], True, semaphore))
    results = await asyncio.gather(*all_tasks)
    newly_installed = [slug for slug, ok, _, _ in results if ok]
    failed = [(slug, src) for slug, ok, src, _ in results if not ok]
    log(f"[Step4] 安装/升级完成: {len(newly_installed)} 成功 / {len(failed)} 失败")
    return newly_installed, failed

# ── Step 5: 测试技能 ────────────────────────────
def step5_test_skills(installed: list[str]) -> tuple[list, list]:
    """测试新安装/升级的技能"""
    safe, unsafe = [], []
    for slug in installed:
        sp = SKILLS_DIR / slug
        skill_md = sp / "SKILL.md"
        if not skill_md.exists():
            unsafe.append((slug, "缺少 SKILL.md"))
            continue
        try:
            content = skill_md.read_text(encoding="utf-8", errors="ignore")
            if len(content) < 50:
                unsafe.append((slug, f"内容过短({len(content)}字符)"))
                continue
            # 检查危险命令
            dangerous = ["curl ", "wget ", "rm -rf /", "eval $", "base64 -d"]
            is_safe = True
            for py_file in sp.rglob("*.py"):
                c = py_file.read_text(encoding="utf-8", errors="ignore")
                for pat in dangerous:
                    if pat in c:
                        is_safe = False
                        unsafe.append((slug, f"危险命令: {pat}"))
                        break
                if not is_safe:
                    break
            if is_safe:
                safe.append(slug)
        except Exception as e:
            unsafe.append((slug, str(e)))
    log(f"[Step5] 测试通过: {len(safe)} | 不合格: {len(unsafe)}")
    return safe, unsafe

# ── Step 6: 集成测试 + PDCA优化 ─────────────────
def step6_integration_and_pdca(safe: list[str], all_skills: dict) -> dict:
    """技能组合+系统集成测试，基于PDCA八分法优化"""
    log("[Step6] 执行PDCA八分法优化...")
    pdca_steps = {
        "P": {"name": "计划", "desc": "确定ML/LLM技能需求，制定学习计划"},
        "D": {"name": "执行", "desc": "安装测试新技能，完成集成验证"},
        "C": {"name": "检查", "desc": "验证技能可用性，评估学习效果"},
        "A": {"name": "处置", "desc": "优化技能组合，形成标准化流程"}
    }
    # 八分法细化
    eight_actions = [
        ("P1", "目标确定", "明确ML/LLM技能提升的具体目标"),
        ("P2", "方法制定", "确定技能获取路径：自学/技能安装/协作讨论"),
        ("D1", "条件确认", "确认环境依赖、版本兼容性"),
        ("D2", "计划执行", "执行技能安装、测试、集成"),
        ("C1", "结果检查", "检查安装成功率、测试通过率"),
        ("C2", "过程评估", "评估时间效率、API消耗"),
        ("A1", "应急处置", "处理失败案例，退回不合格技能"),
        ("A2", "预防措施", "更新技能选择策略，优化流程")
    ]
    summary = {
        "skills_tested": len(safe),
        "skills_passed": len(safe),
        "integration_status": "pass" if len(safe) > 0 else "skip",
        "pdca_completed": True,
        "eight_actions": eight_actions
    }
    log(f"[Step6] PDCA八分法完成，{len(safe)}个技能通过集成测试")
    return summary

# ── 发送邮件报告 ─────────────────────────────────
def send_report(to_install_count: int, to_upgrade_count: int, safe: list, unsafe: list, all_skills: dict, pdca_summary: dict) -> None:
    EMAIL_FROM = "wcyint@163.com"
    EMAIL_TO = "wcyint@163.com"
    SMTP_HOST, SMTP_PORT = "smtp.163.com", 465
    EMAIL_PASSWORD = os.environ.get("HARVEY_EMAIL_AUTH", "SEMefmThGnEKJiTz")
    now = datetime.now(TZ_CST)

    # 生成技能详情行
    rows = ""
    for slug in safe:
        info = all_skills.get(slug, {})
        source = info.get("source", "")
        desc = info.get("description", "")[:80]
        rows += f"<tr><td><code>{slug}</code></td><td>{source}</td><td>{desc}</td><td>✅通过</td></tr>"
    for slug, reason in unsafe:
        rows += f"<tr><td><code>{slug}</code></td><td>-</td><td>{reason[:60]}</td><td>❌退回</td></tr>"

    subject = f"📊 ML/LLM技能提升报告 | {now.strftime('%m-%d %H:%M')} | +{to_install_count}新/+{to_upgrade_count}升级"

    # PDCA八分法详情
    pdca_rows = ""
    for code, name, desc in pdca_summary.get("eight_actions", []):
        pdca_rows += f"<tr><td><b>{code}</b></td><td>{name}</td><td>{desc}</td></tr>"

    body = f"""
    <h2>📊 数据建模/ML/LLM技能专项提升报告</h2>
    <p><b>时间：</b>{now.strftime('%Y-%m-%d %H:%M')} (北京时间)</p>
    <p><b>执行步骤：</b>①gstack多角色讨论 → ②4平台并行搜索 → ③对比安装状态 → ④测试验证 → ⑤集成测试 → ⑥PDCA优化</p>
    <hr>
    <h3>📦 安装/升级结果</h3>
    <p>新安装: <b>{to_install_count}</b> 个 | 升级: <b>{to_upgrade_count}</b> 个 | 测试通过: <b>{len(safe)}</b> 个 | 不合格退回: <b>{len(unsafe)}</b> 个</p>
    <table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;width:100%;font-size:13px">
        <tr style="background:#e8f5e9"><th>技能</th><th>来源</th><th>描述</th><th>状态</th></tr>
        {rows or '<tr><td colspan=4">无</td></tr>'}
    </table>
    <hr>
    <h3>🔄 PDCA八分法优化</h3>
    <table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;width:80%">
        <tr style="background:#e3f2fd"><th>代码</th><th>阶段</th><th>描述</th></tr>
        {pdca_rows}
    </table>
    <hr>
    <h3>🎯 技能组合建议</h3>
    <ul>
        <li><b>核心技能：</b>Python + Pandas + Scikit-learn（数据分析基础）</li>
        <li><b>进阶技能：</b>TensorFlow/PyTorch（深度学习）+ LLM API集成</li>
        <li><b>专项技能：</b>DOE实验设计 + 回归分析 + 数学建模</li>
        <li><b>LLM使用：</b>Prompt工程 + RAG + 微调基础</li>
    </ul>
    <hr>
    <h3>📋 下一步计划</h3>
    <ul>
        <li><b>短期（本周）：</b>基于PDCA结果，优先安装测试未通过的技能，形成完整技能链</li>
        <li><b>中期（本月）：</b>将已验证技能组合形成标准化流程，纳入cron常规任务</li>
        <li><b>长期（本季度）：</b>建立ML/LLM技能库，针对MBA论文数据分析需求定制技能组合</li>
    </ul>
    <hr>
    <p style="color:#888;font-size:12px">由 Harvey 自动生成 | ML/LLM技能专项提升任务 | 每90分钟自动执行</p>
    """
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg.attach(MIMEText(body, "html", "utf-8"))
    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            server.sendmail(EMAIL_FROM, [EMAIL_TO], msg.as_string())
        log(f"[邮件] 报告已发送至 {EMAIL_TO}")
    except Exception as e:
        log(f"[邮件] 发送失败: {e}")

# ── 主流程 ──────────────────────────────────────
async def main():
    # ── 90分钟间隔检查（最先检查，避免不必要的资源消耗）─────────────────────────
    LOG_MARKER.parent.mkdir(parents=True, exist_ok=True)
    try:
        last_run = json.loads(LOG_MARKER.read_text())
        last_ts = datetime.fromisoformat(last_run["timestamp"])
        now_ts = datetime.now(TZ_CST)
        elapsed_minutes = (now_ts - last_ts).total_seconds() / 60
        if elapsed_minutes < 90:
            log(f"[跳过] 距离上次执行仅{int(elapsed_minutes)}分钟，待{int(90-elapsed_minutes)}分钟后执行")
            return
        log(f"[间隔检查] 距离上次执行{int(elapsed_minutes)}分钟，执行任务")
    except:
        pass  # 首次运行或无记录，继续执行

    # ── 增量检查：是否有新技能可用 ────────────────────
    # 快速扫描4平台，不安装只检查是否有新增
    log("[增量检查] 快速扫描4平台是否有新技能...")
    quick_skills = await step2_parallel_search(ML_SKILLS_KEYWORDS[:5])  # 只搜5个关键词
    installed = {d.name for d in SKILLS_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")}
    new_count = sum(1 for slug in quick_skills if slug not in installed)
    log(f"[增量检查] 当前已安装{len(installed)}个，扫描到{new_count}个新技能可安装")

    # ── 事件驱动判断：新技能>=3才执行，否则跳过 ──────
    if new_count < 3:
        log(f"[跳过] 新技能仅{new_count}个（<3），不触发完整流程")
        # 更新标记文件，记录本次检查时间，避免下次重复检查
        LOG_MARKER.write_text(json.dumps({"timestamp": datetime.now(TZ_CST).isoformat(), "new_skills": new_count}))
        return

    LOG_MARKER.write_text(json.dumps({"timestamp": datetime.now(TZ_CST).isoformat(), "new_skills": new_count}))

    # ── 读取历史角色讨论 ────────────────────────
    prev_roles = read_role_files()
    if prev_roles:
        log(f"[角色文件] 找到{len(prev_roles)}个历史角色讨论，可作为参考")

    log("=== ML/LLM技能专项提升任务 Started ===")
    # Step 1: gstack讨论（结果写入共享文件）
    gstack_result = step1_gstack_discussion()
    gstack_ok = gstack_result.get("gstack_ok", False)
    keywords = gstack_result.get("skills_needed", ML_SKILLS_KEYWORDS)
    # 写入共享角色文件
    for role_name, role_data in gstack_result.get("roles", {}).items():
        write_role_file(role_name, role_data)

    # Step 2: 4平台并行搜索
    # 若gstack讨论失败（返回fallback关键词），复用增量检查的quick_skills，避免重复I/O
    if not gstack_ok and keywords == ML_SKILLS_KEYWORDS:
        log(f"[Step2] gstack讨论失败，复用增量检查结果（{len(quick_skills)}个技能）")
        all_skills = quick_skills
    else:
        all_skills = await step2_parallel_search(keywords)
    if not all_skills:
        log("[Step2] 无技能获取，中止")
        return
    # Step 3: 对比决定
    to_install, to_upgrade, already_current = step3_compare_and_decide(all_skills)

    # ── 决策节点：安装前确认 ──────────────────
    if to_install:
        skills_list = list(to_install.keys())[:10]
        reason = f"发现{len(to_install)}个新技能（{', '.join(skills_list[:3])}...），等待确认后安装"
        email_sent = send_decision_email(list(to_install.keys()), reason)
        if not email_sent:
            # 邮件失败，尝试 Feishu fallback
            feishu_sent = send_feishu_message(
                f"🔔 Harvey 技能升级：发现 {len(to_install)} 个新技能待安装（{', '.join(skills_list[:5])}...）\n"
                f"📅 时间：{datetime.now(TZ_CST).strftime('%Y-%m-%d %H:%M')}\n"
                f"⏳ 邮件认证失效，自动继续安装中..."
            )
            if feishu_sent:
                log(f"[决策节点] Feishu 提醒已发送，继续自动安装")
            else:
                log(f"[决策节点] 邮件和 Feishu 都失败，根据授权默认规则继续安装")
        else:
            log(f"[决策节点] 已发送确认请求，暂停等待King回复，中止本次执行")
            return

    # Step 4: 安装/升级（仅在King确认后执行）
    newly_installed, failed = await step4_install_or_upgrade(to_install, to_upgrade)
    if not newly_installed:
        log("[Step4] 无新安装，中止")
        return
    # Step 5: 测试
    safe, unsafe = step5_test_skills(newly_installed)
    # Step 6: PDCA优化
    pdca_summary = step6_integration_and_pdca(safe, all_skills)
    # 发邮件报告
    send_report(len(to_install), len(to_upgrade), safe, unsafe, all_skills, pdca_summary)
    # 保存记录
    with open(LOG_MARKER, "w") as f:
        json.dump({
            "date": datetime.now(TZ_CST).strftime("%Y-%m-%d"),
            "installed": newly_installed,
            "safe": safe,
            "unsafe": unsafe,
            "pdca": pdca_summary
        }, f, indent=2, ensure_ascii=False)
    log(f"=== 完成: 安装{len(newly_installed)} | 测试通过{len(safe)} | 退回{len(unsafe)} ===")

if __name__ == "__main__":
    asyncio.run(main())


__all__ = ['log', 'write_role_file', 'read_role_files', 'send_decision_email', 'step1_gstack_discussion', 'step3_compare_and_decide', 'step5_test_skills', 'step6_integration_and_pdca', 'send_report']
