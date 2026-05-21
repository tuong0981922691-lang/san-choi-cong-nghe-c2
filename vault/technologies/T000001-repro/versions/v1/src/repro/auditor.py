"""Scan an evidence directory and summarize the repro records found."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

import yaml

from . import REPRO_VERSION


@dataclass
class AuditEntry:
    path: str
    status: str
    exit_code: int | None
    argv: list[str]
    recorded_at: str
    git_head: str | None
    git_dirty: bool | None
    issues: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AuditReport:
    total: int
    ok_count: int
    error_count: int
    timeout_count: int
    missing_command_count: int
    dirty_git_count: int
    schema_invalid_count: int
    entries: list[AuditEntry]

    def to_dict(self) -> dict[str, Any]:
        return {
            "total": self.total,
            "ok_count": self.ok_count,
            "error_count": self.error_count,
            "timeout_count": self.timeout_count,
            "missing_command_count": self.missing_command_count,
            "dirty_git_count": self.dirty_git_count,
            "schema_invalid_count": self.schema_invalid_count,
            "entries": [e.to_dict() for e in self.entries],
        }


def _audit_one(path: Path) -> AuditEntry:
    issues: list[str] = []
    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as exc:
        return AuditEntry(
            path=str(path),
            status="schema_invalid",
            exit_code=None,
            argv=[],
            recorded_at="",
            git_head=None,
            git_dirty=None,
            issues=[f"yaml parse error: {exc}"],
        )

    if not isinstance(data, dict):
        return AuditEntry(
            path=str(path),
            status="schema_invalid",
            exit_code=None,
            argv=[],
            recorded_at="",
            git_head=None,
            git_dirty=None,
            issues=["root is not a mapping"],
        )

    if data.get("repro_version") != REPRO_VERSION:
        issues.append(
            f"repro_version mismatch: expected {REPRO_VERSION!r}, "
            f"found {data.get('repro_version')!r}"
        )

    command = data.get("command") or {}
    argv = command.get("argv") or []
    result = data.get("result") or {}
    git = data.get("git") or {}

    status = result.get("status") or "unknown"
    if status not in {"ok", "error", "timeout", "missing_command"}:
        issues.append(f"unknown status: {status!r}")

    if git.get("dirty") is True:
        issues.append("recorded on dirty git working tree")

    return AuditEntry(
        path=str(path),
        status=status if not issues or status in {"ok", "error", "timeout", "missing_command"} else "schema_invalid",
        exit_code=result.get("exit_code"),
        argv=list(argv) if isinstance(argv, list) else [],
        recorded_at=str(data.get("recorded_at") or ""),
        git_head=git.get("head"),
        git_dirty=git.get("dirty"),
        issues=issues,
    )


def audit(directory: Path | str) -> AuditReport:
    """Walk *directory* and produce a summary of every ``*.repro.yaml`` found."""
    d = Path(directory).resolve()
    if not d.is_dir():
        raise NotADirectoryError(f"audit path '{d}' is not a directory")

    entries = [_audit_one(p) for p in sorted(d.rglob("*.repro.yaml"))]
    ok_count = sum(1 for e in entries if e.status == "ok" and not e.issues)
    error_count = sum(1 for e in entries if e.status == "error")
    timeout_count = sum(1 for e in entries if e.status == "timeout")
    missing_count = sum(1 for e in entries if e.status == "missing_command")
    dirty_count = sum(1 for e in entries if e.git_dirty is True)
    schema_invalid = sum(1 for e in entries if e.status == "schema_invalid")

    return AuditReport(
        total=len(entries),
        ok_count=ok_count,
        error_count=error_count,
        timeout_count=timeout_count,
        missing_command_count=missing_count,
        dirty_git_count=dirty_count,
        schema_invalid_count=schema_invalid,
        entries=entries,
    )
