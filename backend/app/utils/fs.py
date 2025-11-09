"""Filesystem utilities"""
import os
import shutil
from pathlib import Path
from typing import Optional


def ensure_dir(path: str | Path) -> Path:
    """Ensure directory exists"""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def safe_rel_path(base: str | Path, target: str | Path) -> Optional[Path]:
    """Get relative path ensuring it's within base directory"""
    try:
        base_path = Path(base).resolve()
        target_path = Path(target).resolve()
        rel_path = target_path.relative_to(base_path)
        return rel_path
    except ValueError:
        # target is not relative to base
        return None


def copy_file(src: str | Path, dst: str | Path) -> None:
    """Copy file ensuring destination directory exists"""
    dst_path = Path(dst)
    ensure_dir(dst_path.parent)
    shutil.copy2(src, dst)


def move_file(src: str | Path, dst: str | Path) -> None:
    """Move file ensuring destination directory exists"""
    dst_path = Path(dst)
    ensure_dir(dst_path.parent)
    shutil.move(str(src), str(dst))


def get_file_size(path: str | Path) -> int:
    """Get file size in bytes"""
    return os.path.getsize(path)
