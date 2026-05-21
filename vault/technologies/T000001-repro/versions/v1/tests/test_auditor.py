"""Tests for repro.auditor.audit()."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from repro.recorder import record, write_record
from repro.auditor import audit


def _seed(tmp_path: Path) -> Path:
    evdir = tmp_path / "evidence"
    evdir.mkdir()

    # 1. ok run
    ok = record([sys.executable, "-c", "print('ok')"], cwd=tmp_path)
    write_record(ok, evdir / "ok.repro.yaml")

    # 2. error run
    err = record(
        [sys.executable, "-c", "import sys; sys.exit(3)"], cwd=tmp_path
    )
    write_record(err, evdir / "err.repro.yaml")

    # 3. timeout run
    to = record(
        [sys.executable, "-c", "import time; time.sleep(5)"],
        cwd=tmp_path,
        timeout_s=1,
    )
    write_record(to, evdir / "timeout.repro.yaml")

    return evdir


def test_audit_counts_status_buckets(tmp_path: Path):
    evdir = _seed(tmp_path)
    report = audit(evdir)
    assert report.total == 3
    assert report.ok_count == 1
    assert report.error_count == 1
    assert report.timeout_count == 1


def test_audit_flags_schema_invalid(tmp_path: Path):
    evdir = tmp_path / "evidence"
    evdir.mkdir()
    (evdir / "bad.repro.yaml").write_text(
        "this: is: not valid yaml: [", encoding="utf-8"
    )
    report = audit(evdir)
    assert report.total == 1
    assert report.schema_invalid_count == 1
    assert report.entries[0].issues  # should report parse error


def test_audit_flags_unknown_repro_version(tmp_path: Path):
    evdir = tmp_path / "evidence"
    evdir.mkdir()
    rec = record([sys.executable, "-c", "print('a')"], cwd=tmp_path)
    rec["repro_version"] = "999"
    write_record(rec, evdir / "future.repro.yaml")

    report = audit(evdir)
    assert any(
        "repro_version mismatch" in issue
        for entry in report.entries
        for issue in entry.issues
    )


def test_audit_empty_dir(tmp_path: Path):
    evdir = tmp_path / "evidence"
    evdir.mkdir()
    report = audit(evdir)
    assert report.total == 0
    assert report.entries == []


def test_audit_raises_on_missing_dir(tmp_path: Path):
    with pytest.raises(NotADirectoryError):
        audit(tmp_path / "nope")


def test_audit_ignores_non_repro_files(tmp_path: Path):
    evdir = tmp_path / "evidence"
    evdir.mkdir()
    (evdir / "readme.txt").write_text("hello", encoding="utf-8")
    (evdir / "summary.md").write_text("# hi", encoding="utf-8")
    report = audit(evdir)
    assert report.total == 0


def test_audit_to_dict_serializable(tmp_path: Path):
    evdir = _seed(tmp_path)
    report = audit(evdir)
    d = report.to_dict()
    # Must be plain dicts/lists/scalars — round-trip through json
    import json
    json.dumps(d)
    assert d["total"] == 3
