from pathlib import Path


def build_review_payload(project_root: Path, version_dir: Path, task: dict, dev_plan: str, code: str) -> dict:
    return {
        'action': 'review',
        'project_root': str(project_root),
        'version_dir': str(version_dir),
        'task': task,
        'dev_plan': dev_plan,
        'code': code,
    }
