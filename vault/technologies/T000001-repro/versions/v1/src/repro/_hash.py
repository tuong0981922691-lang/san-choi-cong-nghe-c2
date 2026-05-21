"""SHA-256 helpers — file content, stream content, deterministic dict serialization."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

_CHUNK = 1024 * 1024  # 1 MiB


def file_sha256(path: Path) -> str:
    """SHA-256 of a file's bytes. Raises FileNotFoundError if missing."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(_CHUNK)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def bytes_sha256(data: bytes) -> str:
    """SHA-256 of an in-memory byte string."""
    return hashlib.sha256(data).hexdigest()


def text_sha256(text: str) -> str:
    """SHA-256 of a UTF-8-encoded text string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_dict_sha256(data: Any) -> str:
    """SHA-256 of a Python value's canonical JSON serialization.

    Uses sorted keys, no extra whitespace, ensure_ascii=False so the hash
    is stable across platforms and Python builds.
    """
    canon = json.dumps(
        data, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    return text_sha256(canon)
