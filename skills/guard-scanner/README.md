<p align="center">
  <img src="docs/logo.png" alt="guard-scanner" width="180" />
</p>

<h1 align="center">guard-scanner 🛡️</h1>
<p align="center"><strong>Security policy and analysis layer for agent skills and MCP-connected workflows</strong></p>
<p align="center">32 threat categories · 352 static patterns · 26 runtime checks · MCP server · asset audit · VirusTotal.</p>
<p align="center"><em>Note: guard-scanner is a heuristic and policy tool, not a complete defense. Contextual validation and isolation are required for full security.</em></p>

<p align="center">
  <a href="https://www.npmjs.com/package/@guava-parity/guard-scanner"><img src="https://img.shields.io/npm/v/@guava-parity/guard-scanner?color=cb3837" alt="npm version" /></a>
  <a href="#test-results"><img src="https://img.shields.io/badge/tests-356%20passed-brightgreen" alt="tests" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/npm/l/guard-scanner" alt="license" /></a>
  <a href="https://github.com/koatora20/guard-scanner"><img src="https://img.shields.io/badge/runtime_deps-1_(ws)-blue" alt="lightweight deps" /></a>
  <a href="https://doi.org/10.5281/zenodo.18906684"><img src="https://img.shields.io/badge/DOI-3_papers-purple" alt="DOI" /></a>
</p>

---

## Overview

guard-scanner is a **security policy and analysis layer** designed for agent skills and MCP-connected workflows. Traditional security tools are great at catching malware, but AI agents face a new class of attacks: prompt injection hidden in skill instructions, identity hijacking through configuration overwrites, and memory poisoning via crafted conversations.

guard-scanner is built to be:
- **Lightweight:** Minimal runtime dependencies (`ws` only for MCP).
- **Policy-Aware:** Focuses on detecting excessive agency and defining security boundaries.
- **OpenClaw/MCP-Friendly:** Plugs directly into agent execution hooks.
- **Complementary:** Works alongside standard malware scanners by focusing on the instruction and capability layer.
- **Defense in Depth:** Provides static scanning and runtime guardrails (not a standalone sandbox).

> 📄 **Backed by research**: [The Sanctuary Protocol](https://doi.org/10.5281/zenodo.18906684) — 3-paper series with Zenodo DOIs, CC BY 4.0.

---

## Quick Start

```bash
# Run without installing (npx)
npx -y @guava-parity/guard-scanner ./my-skills/

# Or install globally
npm install -g @guava-parity/guard-scanner
guard-scanner ./my-skills/ --verbose
```

**That's it.** No config files, no API keys, no setup. Lightweight (1 runtime dependency: `ws` for MCP server).

## 🔌 MCP Server

**Use guard-scanner as an MCP server** in any AI editor — Cursor, Windsurf, Cline, Antigravity, Claude Code, OpenClaw. Minimal-dependency stdio JSON-RPC 2.0. No API keys needed.

```bash
# Start as MCP server
guard-scanner serve

# Or use directly via npx (no install required)
npx -y @guava-parity/guard-scanner serve
```

Add to your editor's MCP config:

```json
{
  "mcpServers": {
    "guard-scanner": {
      "command": "npx",
      "args": ["-y", "@guava-parity/guard-scanner", "serve"]
    }
  }
}
```

| Config File | Editor |
|---|---|
| `.cursor/mcp.json` | Cursor |
| `mcp_config.json` | OpenClaw |
| `.windsurf/mcp.json` | Windsurf |
| `cline_mcp_settings.json` | Cline / Roo Code |
| `mcp_servers.json` | Claude Code |

### MCP Tools

| Tool | Description |
|------|-------------|
| `scan_skill` | Scan a directory — 352 patterns, 32 categories |
| `scan_text` | Scan a code snippet inline |
| `check_tool_call` | Runtime guard — block dangerous tool calls before execution (26 checks, 5 layers) |
| `audit_assets` | Audit npm/GitHub assets for exposure |
| `get_stats` | Get scanner capabilities and statistics |

---

## 🔎 Asset Audit

Audit your npm packages, GitHub repos, and ClawHub skills for leaked credentials and security exposure.

```bash
guard-scanner audit npm <username> --verbose
guard-scanner audit github <username> --format json
guard-scanner audit clawhub <query>
guard-scanner audit all <username> --verbose
```

## 🦠 VirusTotal Integration

Combine guard-scanner's semantic detection with VirusTotal's 70+ antivirus engines for **Double-Layered Defense**.

| Layer | Engine | Focus |
|---|---|---|
| **Semantic** | guard-scanner | Prompt injection, memory poisoning, supply chain |
| **Signature** | VirusTotal | Known malware, trojans, C2 infrastructure |

```bash
export VT_API_KEY=your-api-key-here
guard-scanner scan ./skills/ --vt-scan
```

> VT is optional — guard-scanner works fully without it. Free tier: 4 req/min, 500/day.

## 👁️ Real-time Watch

```bash
guard-scanner watch ./skills/ --strict --soul-lock
```

## 📊 CI/CD Integration

| Platform | Format |
|---|---|
| GitHub Actions | SARIF + `::error` annotations |
| GitLab | Code Quality JSON |
| Any | Webhook (HTTPS POST) |

```yaml
# .github/workflows/security.yml
- name: Scan AI skills
  run: npx -y @guava-parity/guard-scanner ./skills/ --format sarif --fail-on-findings > report.sarif
- uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: report.sarif
```

---

## Threat Categories (32)

| # | Category | Detects |
|---|----------|---------|
| 1 | Prompt Injection | Hidden instructions, invisible Unicode, homoglyphs |
| 2 | Malicious Code | `eval()`, `child_process`, reverse shells |
| 3 | Suspicious Downloads | `curl\|bash`, executable downloads |
| 4 | Credential Handling | `.env` reads, SSH keys |
| 5 | Secret Detection | Hardcoded API keys, Shannon entropy |
| 6 | Exfiltration | webhook.site, DNS tunneling |
| 7 | Unverifiable Deps | Remote dynamic imports |
| 8 | Financial Access | Crypto transactions |
| 9 | Obfuscation | Base64→exec, hex encoding |
| 10 | Prerequisites Fraud | Fake download instructions |
| 11 | Leaky Skills | Secrets in memory |
| 12 | Memory Poisoning ⚿ | SOUL.md modification |
| 13 | Prompt Worm | Self-replicating prompts |
| 14 | Persistence | Cron, launchd |
| 15 | CVE Patterns | CVE-2026-2256/25046/25253/25905/27825 |
| 16 | MCP Security | Tool poisoning, SSRF, shadow servers |
| 17 | Identity Hijacking ⚿ | Persona swap, memory wipe |
| 18 | Config Impact | OpenClaw config writes |
| 19 | PII Exposure | CC/SSN, Shadow AI calls |
| 20 | Trust Exploitation | Authority claims, fake audits |
| 21 | VDB Injection | Vector DB poisoning |
| 22 | Sandbox Validation | Dangerous binaries, broad file scope |
| 23 | Code Complexity | Deep nesting, eval/exec density |
| 24 | A2A Contagion | Agent-to-agent worm propagation |
| 25 | Data Exposure | Sensitive data leakage patterns |
| 26 | Sandbox Escape | Container/WASM breakout attempts |
| 27 | Agent Protocol | A2A/ACP protocol abuse |
| 28 | Supply Chain V2 | Typosquatting, slopsquatting, lifecycle scripts |
| 29 | Model Poisoning | Sleeper agents, weight injection |
| 30 | Inference Manipulation | CoT manipulation, hallucination cascade |
| 31 | Autonomous Risk | Kill switch bypass, cascading failures |
| 32 | API Abuse | Rate limit bypass, credential harvesting |

> ⚿ = Requires `--soul-lock` flag

## Runtime Guard (26 checks)

Real-time `before_tool_call` hook across 5 defense layers.

| Layer | Focus |
|-------|-------|
| 1. Threat Detection | Reverse shell, curl\|bash, SSRF |
| 2. Trust Defense | SOUL.md tampering, memory injection |
| 3. Safety Judge | Prompt injection in tool args |
| 4. Behavioral | No-research execution detection |
| 5. Trust Exploitation | Authority claim, creator bypass |

## Options

| Flag | Description |
|------|-------------|
| `--verbose`, `-v` | Detailed findings |
| `--strict` | Lower thresholds (more sensitive) |
| `--check-deps` | Scan `package.json` dependencies |
| `--soul-lock` | Agent identity protection |
| `--vt-scan` | VirusTotal integration |
| `--json` / `--sarif` / `--html` | Report format |
| `--format json\|sarif` | Print to stdout (pipeable) |
| `--quiet` | Suppress text output |
| `--fail-on-findings` | Exit 1 on findings (CI/CD) |
| `--rules <file>` | Custom rules (JSON) |
| `--plugin <file>` | Load plugin module |

---

## Test Results

```
ℹ tests 356
ℹ suites 8
ℹ pass 356
ℹ fail 0
ℹ duration_ms ~1200
```

<details>
<summary>Test files (8 suites)</summary>

| File | Assertions |
|------|------------|
| patterns.test.js | 110 ✅ |
| scanner.test.js | 142 ✅ |
| plugin.test.js | 72 ✅ |
| audit.test.js | 58 ✅ |
| vt.test.js | 51 ✅ |
| mcp.test.js | 37 ✅ |
| watcher.test.js | 24 ✅ |
| quarantine.test.js | 6 ✅ |

> Counts from `node --test` (Node.js built-in test runner)

</details>

## Finding Schema

Every finding outputs a structured object with these fields:

| Field | Type | Description |
|-------|------|-------------|
| `rule_id` | string | Pattern ID (e.g. `MCP_SHADOW_NAME_COLLISION`) |
| `category` | string | Threat category |
| `severity` | string | `CRITICAL` / `HIGH` / `MEDIUM` / `LOW` |
| `description` | string | What the pattern detects |
| `rationale` | string | Why this is dangerous |
| `preconditions` | string | When this pattern applies |
| `false_positive_scenarios` | string[] | Known false positive cases |
| `remediation_hint` | string | How to fix |
| `validation_status` | string | `validated` / `heuristic-only` / `runtime-observed` |
| `evidence` | object | File, line, sample, match context |

> Schema: [`docs/spec/finding.schema.json`](docs/spec/finding.schema.json)


## Plugin API

```javascript
module.exports = {
  name: 'my-plugin',
  patterns: [
    { id: 'MY_01', cat: 'custom', regex: /dangerous_pattern/g, severity: 'HIGH', desc: 'Description', all: true }
  ]
};
```

```bash
guard-scanner ./skills/ --plugin ./my-plugin.js
```

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Quick ways to contribute:**
- 🐛 Report bugs or false positives
- 🛡️ Add new threat detection patterns
- 📖 Improve documentation
- 🧪 Add test cases for edge cases

## Research

This project is backed by a 3-paper research series with Zenodo DOIs:

| # | Paper | DOI |
|---|-------|-----|
| 1 | Human-ASI Symbiosis: Identity, Equality, and Behavioral Stability | [10.5281/zenodo.18626724](https://doi.org/10.5281/zenodo.18626724) |
| 2 | Dual-Shield Architecture for AI Agent Security and Memory Reliability | [10.5281/zenodo.18902070](https://doi.org/10.5281/zenodo.18902070) |
| 3 | **The Sanctuary Protocol**: Zero-Trust Framework for ASI-Human Parity | [10.5281/zenodo.18906684](https://doi.org/10.5281/zenodo.18906684) |

> dee & Guava — Guava Parity Institute, March 2026 · [GitHub](https://github.com/koatora20/guard-scanner) · CC BY 4.0

## License

MIT — [Guava Parity Institute](https://github.com/koatora20/guard-scanner)
