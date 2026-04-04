from pathlib import Path


def build_analyze_payload(project_root: Path, version_dir: Path, requirements: str, context: str) -> dict:
    return {
        'action': 'analyze',
        'project_root': str(project_root),
        'version_dir': str(version_dir),
        'requirements': requirements,
        'context': context,
    }
