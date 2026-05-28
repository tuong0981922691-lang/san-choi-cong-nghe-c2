"""Git HEAD + dirty-flag probe. No-op (returns ``None``) when not in a git repo."""

from __future__ import annotations

from pathlib import Path
from subprocess import run, PIPE, STDOUT, TimeoutExpired, CompletedProcess
from typing import Any

_GIT_TIMEOUT_S = 10


def _git(args: list[str], cwd: Path) -> CompletedProcess | None:
    try:
        return run(
            ["git", *args],
            cwd=str(cwd),
            stdout=PIPE,
            stderr=STDOUT,
            timeout=_GIT_TIMEOUT_S,
            check=False,
        )
    except (TimeoutExpired, FileNotFoundError, OSError):
        return None


def head_commit(cwd: Path) -> str | None:
    r = _git(["rev-parse", "HEAD"], cwd)
    if r is None or r.returncode != 0:
        return None
    return r.stdout.decode("utf-8", errors="replace").strip()


def is_dirty(cwd: Path) -> bool | None:
    """True iff there are tracked-file modifications. None if unknown."""
    r = _git(["status", "--porcelain"], cwd)
    if r is None or r.returncode != 0:
        return None
    out = r.stdout.decode("utf-8", errors="replace").strip()
    return bool(out)


def collect_git(cwd: Path) -> dict[str, Any]:
    """Bundle git fingerprint. Missing fields stay ``None``."""
    return {
        "head": head_commit(cwd),
        "dirty": is_dirty(cwd),
    }
