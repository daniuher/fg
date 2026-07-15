from datetime import datetime, timezone
from pathlib import Path
from fg.core.hashing import compute_hash


def get_metadata(filepath: str | Path) -> dict:
    p = Path(filepath).expanduser().resolve()
    if not p.exists():
        raise FileNotFoundError(f"No such file: {p}")
    if not p.is_file():
        raise ValueError(f"Not a regular file: {p}")

    stat = p.stat()
    return {
        "hash": compute_hash(p),
        "fullpath": str(p),
        "filename": p.name,
        "extension": p.suffix.lower() or None,
        "size_bytes": stat.st_size,
        "modified_at": datetime.fromtimestamp(
            stat.st_mtime, tz=timezone.utc
        ).isoformat(),
        "registered_at": datetime.now(tz=timezone.utc).isoformat(),
    }
