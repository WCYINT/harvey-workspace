from __future__ import annotations

from pathlib import Path

from llm import OpenAICompatibleLLM
from project import scan_project_files, get_current_version_dir
from state import StateManager


DEFAULT_SCAN_LIMITS = {
    'analyze': 10,
    'write': 8,
    'review': 10,
    'fix': 8,
}


def _truncate_preview(text: str, limit: int = 160) -> str:
    text = text.replace('\n', ' ').strip()
    return text[:limit] + ('...' if len(text) > limit else '')


def estimate_llm_risk(project_root: Path, config: dict, action: str) -> dict:
    limit = DEFAULT_SCAN_LIMITS.get(action, 8)
    files = scan_project_files(project_root, limit=limit)

    llm = OpenAICompatibleLLM(config)
    endpoint = f"{llm.base_url}/chat/completions" if llm.base_url else ''
    model = llm.model or ''

    scanned_files = []
    total_chars = 0
    total_bytes = 0

    for f in files:
        content = f.get('content', '')
        chars = len(content)
        b = len(content.encode('utf-8', errors='ignore'))
        total_chars += chars
        total_bytes += b
        scanned_files.append({
            'path': f['path'],
            'chars': chars,
            'bytes': b,
            'preview': _truncate_preview(content),
        })

    return {
        'action': action,
        'scan_limit': limit,
        'file_count': len(scanned_files),
        'total_chars': total_chars,
        'total_bytes': total_bytes,
        'endpoint': endpoint,
        'model': model,
        'files': scanned_files,
    }


def build_llm_risk_lines(risk: dict) -> list[str]:
    lines = []
    lines.append('⚠️ LLM 网络预检')
    lines.append(f"- action: {risk['action']}")
    lines.append(f"- endpoint: {risk['endpoint'] or '-'}")
    lines.append(f"- model: {risk['model'] or '-'}")
    lines.append(f"- files: {risk['file_count']}")
    lines.append(f"- estimated_chars: {risk['total_chars']}")
    lines.append(f"- estimated_bytes: {risk['total_bytes']}")
    if risk['files']:
        lines.append('- scanned_files:')
        for item in risk['files'][:10]:
            lines.append(f"  - {item['path']} ({item['chars']} chars, {item['bytes']} bytes)")
    return lines


def print_llm_risk(risk: dict):
    for line in build_llm_risk_lines(risk):
        print(line)
