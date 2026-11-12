"""Frozen exported entry; external pinning is still the initial trust root."""

import hashlib
from pathlib import Path

path = Path(__file__).absolute().with_name("bootstrap.py")
if path.is_symlink():
    raise RuntimeError("Bootstrap symlink refused")
raw = path.read_bytes()
if (
    hashlib.sha256(raw).hexdigest()
    != "70e03f2215282e2d4aa6fd0a58161ce0b9858981a114caba49f4826f5833599c"
):
    raise RuntimeError("Approved bootstrap bytes changed")
exec(
    compile(raw, str(path), "exec", dont_inherit=True),
    {"__name__": "__main__", "__file__": str(path)},
)
