from pathlib import Path
from nchunk.utils import ensure_posix

def test_ensure_posix_str():
    assert ensure_posix("foo/bar") == "foo/bar"

def test_ensure_posix_path():
    assert ensure_posix(Path("foo") / "bar") == "foo/bar"
