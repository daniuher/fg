import hashlib
from pathlib import Path

def compute_hash(path: Path, chunk_size: int = 65536) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()

if __name__ == "__main__":
    path = Path('/home/duher/Git/priv/fg/pyproject.toml')
    print(path)
    print(compute_hash(path))
