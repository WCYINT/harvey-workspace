from __future__ import annotations

import re
from pathlib import Path


from project_board import DEFAULT_PROJECTS_FILE, find_workspace_root, load_projects


def find_board_path(start: Path | None = None) -> Path:
    workspace_root = find_workspace_root(start)
    return workspace_root / DEFAULT_PROJECTS_FILE


def list_projects(start: Path | None = None) -> list[dict]:
    board_path = find_board_path(start)
    return load_projects(board_path)


def get_project_by_name(name: str, start: Path | None = None) -> dict:
    projects = list_projects(start)
    for project in projects:
        if project['name'] == name:
            return project
    raise RuntimeError(f'项目不存在: {name}')


def parse_version(version: str) -> tuple[int, int, int]:
    m = re.fullmatch(r'v(\d+)\.(\d+)\.(\d+)', version)
    if not m:
        raise RuntimeError(f'非法版本号: {version}，期望形如 v1.2.3')
    return tuple(int(x) for x in m.groups())


def bump_version(version: str, bump: str = 'patch') -> str:
    major, minor, patch = parse_version(version)
    if bump == 'major':
        return f'v{major + 1}.0.0'
    if bump == 'minor':
        return f'v{major}.{minor + 1}.0'
    if bump == 'patch':
        return f'v{major}.{minor}.{patch + 1}'
    raise RuntimeError(f'不支持的 bump 类型: {bump}')
