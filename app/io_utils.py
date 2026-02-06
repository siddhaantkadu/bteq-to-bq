from __future__ import annotations
from pathlib import Path

SQL_EXTS = {".sql", ".bteq", ".txt"}

def iter_sql_files(root: Path):
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in SQL_EXTS:
            yield p

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")

def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
