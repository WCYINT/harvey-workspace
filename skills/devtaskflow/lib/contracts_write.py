from pathlib import Path


def build_write_payload(project_root: Path, version_dir: Path, task: dict, dev_plan: str, context: str) -> dict:
    return {
        'action': 'write',
        'project_root': str(project_root),
        'version_dir': str(version_dir),
        'task': task,
        'dev_plan': dev_plan,
        'context': context,
    }
