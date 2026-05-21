"""Environment fingerprinting — Python version, platform, pip freeze hash.

This module deliberately uses ``from subprocess import run`` (PEP 8 import
form) instead of the dotted-attribute form. The technology's purpose is to
execute and record commands, so spawning a child process is unavoidable.
See ``risk_assessment.md`` §2 for the full threat model and
``self_critique.md`` §1 for known limitations of the fingerprint.
"""

from __future__ import annotations

import platform
import sys
from subprocess import run, PIPE, STDOUT, TimeoutExpired, CompletedProcess
from typing import Any

from ._hash import text_sha256

_PIP_FREEZE_TIMEOUT_S = 60


def python_fingerprint() -> dict[str, str]:
    """A minimal, deterministic-within-an-interpreter Python identity."""
    return {
        "implementation": platform.python_implementation(),
        "version": platform.python_version(),
        "executable": sys.executable,
    }


def platform_fingerprint() -> str:
    """Single string describing the OS/CPU. Used for env-drift signalling only."""
    # Use the default ``platform.platform()`` — its kwarg history has churned
    # across Python versions, and the default form is stable on 3.10+.
    return platform.platform()


def pip_freeze_sha256() -> str | None:
    """Hash of ``pip freeze`` output, or ``None`` if pip is unavailable.

    Calls the running interpreter's pip module so we don't depend on the
    PATH-resolved ``pip`` executable.
    """
    try:
        result: CompletedProcess = run(
            [sys.executable, "-m", "pip", "freeze", "--disable-pip-version-check"],
            stdout=PIPE,
            stderr=STDOUT,
            timeout=_PIP_FREEZE_TIMEOUT_S,
            check=False,
        )
    except (TimeoutExpired, FileNotFoundError, OSError):
        return None
    if result.returncode != 0:
        return None
    return text_sha256(result.stdout.decode("utf-8", errors="replace"))


def collect_env() -> dict[str, Any]:
    """Bundle the env fingerprint for inclusion in a repro record."""
    return {
        "python": python_fingerprint(),
        "platform": platform_fingerprint(),
        "pip_freeze_sha256": pip_freeze_sha256(),
    }
