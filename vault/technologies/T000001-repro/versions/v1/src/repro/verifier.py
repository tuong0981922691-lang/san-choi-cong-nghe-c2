"""Replay a recorded command and report drift vs the stored record."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

import yaml

from . import REPRO_VERSION
from ._hash import file_sha256
from .recorder import record as record_command, INLINE_CAPTURE_LIMIT_BYTES


@dataclass
class VerifyResult:
    """Outcome of comparing a replay against a stored record."""

    ok: bool
    drifts: list[str]  # human-readable list of differences

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _read_record(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"repro file '{path}' does not exist")
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"repro file '{path}' is not a mapping")
    if data.get("repro_version") != REPRO_VERSION:
        raise ValueError(
            f"repro_version mismatch in '{path}': "
            f"expected {REPRO_VERSION!r}, found {data.get('repro_version')!r}"
        )
    return data


def _compare(label: str, expected: Any, actual: Any) -> list[str]:
    if expected != actual:
        return [f"{label}: expected {expected!r}, got {actual!r}"]
    return []


def verify(record_path: Path | str, *, cwd: Path | str | None = None) -> VerifyResult:
    """Replay the command stored in *record_path* and report drift.

    ``cwd`` defaults to the cwd stored in the record. The replay reuses the
    record's argv, timeout, and capture mode verbatim.
    """
    record_path = Path(record_path).resolve()
    stored = _read_record(record_path)

    command = stored.get("command") or {}
    argv = command.get("argv")
    if not isinstance(argv, list) or not argv:
        raise ValueError(f"repro file '{record_path}' has no command.argv")

    effective_cwd = Path(cwd) if cwd is not None else Path(command.get("cwd", "."))
    if not effective_cwd.is_absolute():
        effective_cwd = (record_path.parent / effective_cwd).resolve()

    drifts: list[str] = []

    # 1. Pre-replay: input files must match the recorded hashes.
    for input_entry in stored.get("inputs") or []:
        rel = input_entry["path"]
        expected_sha = input_entry["sha256"]
        actual_path = effective_cwd / rel
        if not actual_path.exists():
            drifts.append(f"input missing: {rel}")
            continue
        actual_sha = file_sha256(actual_path)
        if actual_sha != expected_sha:
            drifts.append(
                f"input changed: {rel} (sha256 {expected_sha[:12]}… → {actual_sha[:12]}…)"
            )

    if drifts:
        # Input drift makes a clean replay impossible — bail without running.
        return VerifyResult(ok=False, drifts=drifts)

    # 2. Replay.
    replay = record_command(
        argv,
        cwd=effective_cwd,
        inputs=[Path(e["path"]) for e in stored.get("inputs") or []],
        timeout_s=command.get("timeout_s", 300),
        capture=command.get("capture", "full"),
    )

    # 3. Compare outcome.
    stored_result = stored.get("result") or {}
    replay_result = replay["result"]

    drifts += _compare("status", stored_result.get("status"), replay_result["status"])
    drifts += _compare(
        "exit_code", stored_result.get("exit_code"), replay_result["exit_code"]
    )
    expected_stdout_sha = (stored_result.get("stdout") or {}).get("sha256")
    actual_stdout_sha = replay_result["stdout"]["sha256"]
    drifts += _compare("stdout.sha256", expected_stdout_sha, actual_stdout_sha)
    expected_stderr_sha = (stored_result.get("stderr") or {}).get("sha256")
    actual_stderr_sha = replay_result["stderr"]["sha256"]
    drifts += _compare("stderr.sha256", expected_stderr_sha, actual_stderr_sha)

    return VerifyResult(ok=not drifts, drifts=drifts)
