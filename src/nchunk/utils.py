
from pathlib import Path
from uuid import uuid4

def generate_chunk_dir(base_url: str, user: str) -> str:
    return f"{base_url.rstrip('/')}/uploads/{user}/{uuid4().hex}"

def ensure_posix(path: Path | str) -> str:
    if isinstance(path, Path):
        return path.as_posix()
    return Path(path).as_posix()
