from __future__ import annotations

from pathlib import Path


DEFAULT_PROJECTS_DIR = 'projects'


def ensure_projects_root(workspace_root: Path) -> Path:
    path = workspace_root / DEFAULT_PROJECTS_DIR
    path.mkdir(parents=True, exist_ok=True)
    return path


def resolve_project_init_path(workspace_root: Path, raw_path: str | None, name: str | None) -> Path:
    if raw_path:
        return Path(raw_path).resolve()
    if not name:
        raise RuntimeError('未提供 --path 时必须提供 --name')
    projects_root = ensure_projects_root(workspace_root)
    return (projects_root / name).resolve()


def guess_workspace_root_for_init(cwd: Path) -> Path:
    candidate = cwd.resolve()
    if (candidate / 'PROJECTS.md').exists() or (candidate / 'AGENTS.md').exists():
        return candidate
    return candidate
