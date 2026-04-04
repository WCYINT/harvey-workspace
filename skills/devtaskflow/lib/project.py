from pathlib import Path


def get_versions_dir(project_root: Path, config: dict):
    return project_root / config['pipeline'].get('versions_dir', 'versions')


def get_current_version_dir(project_root: Path, config: dict):
    versions_dir = get_versions_dir(project_root, config)
    if not versions_dir.exists():
        return None
    version_dirs = [d for d in versions_dir.iterdir() if d.is_dir() and d.name.startswith('v')]
    if not version_dirs:
        return None
    return max(version_dirs, key=lambda d: d.stat().st_mtime)


def scan_project_files(project_root: Path, limit: int = 20):
    files = []
    exclude = {'node_modules', '.git', 'versions', '.dtflow', '__pycache__', '.venv', 'venv'}
    for path in project_root.rglob('*'):
        if not path.is_file():
            continue
        if any(part in exclude for part in path.parts):
            continue
        if path.suffix.lower() not in {'.js', '.ts', '.jsx', '.tsx', '.py', '.md', '.json'}:
            continue
        try:
            files.append({
                'path': str(path.relative_to(project_root)),
                'content': path.read_text(encoding='utf-8', errors='ignore')[:5000],
            })
        except Exception:
            continue
        if len(files) >= limit:
            break
    return files
