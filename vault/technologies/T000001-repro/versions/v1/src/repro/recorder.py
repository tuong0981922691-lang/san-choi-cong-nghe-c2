"""Record a command execution into a structured ``.repro.yaml`` artifact."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path
from subprocess import run, PIPE, STDOUT, TimeoutExpired, CompletedProcess
from typing import Any, Iterable

import yaml

from . import REPRO_VERSION, SCHEMA_VERSION
from ._env import collect_env
from ._git import collect_git
from ._hash import file_sha256, bytes_sha256

DEFAULT_TIMEOUT_S = 300
INLINE_CAPTURE_LIMIT_BYTES = 64 * 1024  # 64 KiB


def _iso_utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _hash_inputs(input_paths: Iterable[Path], cwd: Path) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for raw in input_paths:
        p = (cwd / raw).resolve() if not Path(raw).is_absolute() else Path(raw).resolve()
        # Refuse paths that escape the working tree — defensive only; the
        # caller is trusted but we don't want to silently hash random files.
        try:
            p.relative_to(cwd.resolve())
        except ValueError:
            raise ValueError(
                f"input '{raw}' is outside the working directory '{cwd}'"
            )
        if not p.exists():
            raise FileNotFoundError(f"input '{raw}' does not exist")
        if not p.is_file():
            raise IsADirectoryError(f"input '{raw}' is not a regular file")
        out.append({"path": str(p.relative_to(cwd.resolve())), "sha256": file_sha256(p)})
    return out


def _format_capture(blob: bytes, inline: bool) -> dict[str, Any]:
    sha = bytes_sha256(blob)
    if inline and len(blob) <= INLINE_CAPTURE_LIMIT_BYTES:
        try:
            text = blob.decode("utf-8")
        except UnicodeDecodeError:
            text = None
        return {
            "sha256": sha,
            "bytes": len(blob),
            "text": text,
        }
    return {"sha256": sha, "bytes": len(blob), "text": None}


def record(
    argv: list[str],
    *,
    cwd: Path | str = ".",
    inputs: Iterable[Path] | None = None,
    timeout_s: int = DEFAULT_TIMEOUT_S,
    capture: str = "full",
) -> dict[str, Any]:
    """Run *argv* under *cwd* and return a repro record dict.

    Parameters
    ----------
    argv
        Command vector. Always passed as a list — no shell, no string-splitting.
    cwd
        Working directory; defaults to ``.``.
    inputs
        Paths whose content hashes go into the record. Caller declares the
        files that the command *depends* on.
    timeout_s
        Hard wall-clock cap. Default 300 s.
    capture
        ``"full"`` to inline stdout/stderr up to ``INLINE_CAPTURE_LIMIT_BYTES``,
        ``"hash"`` to keep only the SHA-256.
    """
    if capture not in ("full", "hash"):
        raise ValueError("capture must be 'full' or 'hash'")
    cwd_p = Path(cwd).resolve()
    if not cwd_p.is_dir():
        raise NotADirectoryError(f"cwd '{cwd}' is not a directory")

    inputs_block = _hash_inputs(inputs or [], cwd_p)

    start = time.monotonic()
    status = "ok"
    stdout_bytes = b""
    stderr_bytes = b""
    exit_code: int | None = None
    try:
        proc: CompletedProcess = run(
            argv,
            cwd=str(cwd_p),
            stdout=PIPE,
            stderr=PIPE,
            timeout=timeout_s,
            check=False,
        )
        stdout_bytes = proc.stdout or b""
        stderr_bytes = proc.stderr or b""
        exit_code = proc.returncode
        if exit_code != 0:
            status = "error"
    except TimeoutExpired as exc:
        status = "timeout"
        stdout_bytes = exc.stdout or b""
        stderr_bytes = exc.stderr or b""
        exit_code = None
    except FileNotFoundError as exc:
        status = "missing_command"
        stderr_bytes = str(exc).encode("utf-8")
        exit_code = None
    duration = time.monotonic() - start

    inline = capture == "full"
    record_dict: dict[str, Any] = {
        "repro_version": REPRO_VERSION,
        "schema_version": SCHEMA_VERSION,
        "recorded_at": _iso_utc_now(),
        "command": {
            "argv": list(argv),
            "cwd": str(cwd_p.relative_to(cwd_p)) if cwd_p == Path.cwd().resolve() else str(cwd_p),
            "timeout_s": timeout_s,
            "capture": capture,
        },
        "inputs": inputs_block,
        "env": collect_env(),
        "git": collect_git(cwd_p),
        "result": {
            "status": status,
            "exit_code": exit_code,
            "duration_s": round(duration, 4),
            "stdout": _format_capture(stdout_bytes, inline),
            "stderr": _format_capture(stderr_bytes, inline),
        },
    }
    return record_dict


def write_record(record_dict: dict[str, Any], output_path: Path) -> None:
    """Write a record dict as canonical YAML to *output_path*."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as f:
        yaml.safe_dump(
            record_dict,
            f,
            sort_keys=False,
            allow_unicode=True,
            default_flow_style=False,
            width=4096,
        )
