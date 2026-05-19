from pathlib import Path
from typing import Iterable, List

ALLOWED_EXTENSIONS = {".txt", ".md", ".pdf"}


def is_allowed_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def list_supported_files(folder: Path) -> List[Path]:
    if not folder.exists():
        return []
    files: List[Path] = []
    for path in folder.rglob("*"):
        if path.is_file() and path.suffix.lower() in ALLOWED_EXTENSIONS:
            files.append(path)
    return sorted(files)


def safe_filename(filename: str) -> str:
    """Keep a readable filename while removing dangerous path characters."""
    name = Path(filename).name.strip().replace(" ", "_")
    for ch in ["/", "\\", ":", "*", "?", "\"", "<", ">", "|"]:
        name = name.replace(ch, "_")
    return name or "uploaded_file"


def read_jsonl_tail(path: Path, limit: int = 20) -> list[str]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    return lines[-limit:]
