const fs = require('fs');
const path = require('path');
const { PATTERNS } = require('../src/patterns.js');
const { RUNTIME_CHECKS } = require('../src/runtime-guard.js');
const packageJson = require('../package.json');
const pluginJson = require('../openclaw.plugin.json');

const specDir = path.join(__dirname, '../docs/spec');
const capabilitiesPath = path.join(specDir, 'capabilities.json');

if (!fs.existsSync(specDir)) {
    fs.mkdirSync(specDir, { recursive: true });
}

// Calculate true values from source code
const categories = new Set(PATTERNS.map(p => p.cat));

const spec = {
    package_version: packageJson.version,
    plugin_version: pluginJson.version,
    static_pattern_count: PATTERNS.length,
    threat_category_count: categories.size,
    runtime_check_count: RUNTIME_CHECKS.length,
    test_count: 539, // Static count based on recent run
    test_suite_count: 116,
    dependencies_runtime: Object.keys(packageJson.dependencies || {}).length, // 1 for 'ws'
    dependencies_dev: Object.keys(packageJson.devDependencies || {}).length,
    mcp_tools: ["scan_skill", "scan_text", "check_tool_call", "audit_assets", "get_stats", "task_status", "task_result"],
    cli_commands: ["scan", "serve", "monitor", "audit"],
    supported_outputs: ["json", "sarif", "html", "terminal"],
    supported_integrations: ["openclaw", "mcp", "virustotal", "github", "npm"]
};

fs.writeFileSync(capabilitiesPath, JSON.stringify(spec, null, 2));
console.log(`✅ Generated SSoT at ${capabilitiesPath}`);
console.log(JSON.stringify(spec, null, 2));
