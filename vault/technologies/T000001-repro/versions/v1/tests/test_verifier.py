"""Tests for repro.verifier.verify()."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from repro.recorder import record, write_record
from repro.verifier import verify


def _save(rec: dict, path: Path) -> Path:
    write_record(rec, path)
    return path


def test_verify_deterministic_command(tmp_path: Path):
    rec = record([sys.executable, "-c", "print('hi')"], cwd=tmp_path)
    path = _save(rec, tmp_path / "rec.repro.yaml")
    result = verify(path)
    assert result.ok, f"unexpected drift: {result.drifts}"
    assert result.drifts == []


def test_verify_detects_nondeterminism(tmp_path: Path):
    rec = record(
        [sys.executable, "-c", "import random; print(random.random())"],
        cwd=tmp_path,
    )
    path = _save(rec, tmp_path / "rand.repro.yaml")
    result = verify(path)
    assert not result.ok
    assert any("stdout.sha256" in d for d in result.drifts)


def test_verify_detects_input_drift(tmp_path: Path):
    inp = tmp_path / "data.txt"
    inp.write_text("original", encoding="utf-8")
    rec = record(
        [sys.executable, "-c", "print('ok')"],
        cwd=tmp_path,
        inputs=[inp],
    )
    path = _save(rec, tmp_path / "rec.repro.yaml")

    # Mutate the input file.
    inp.write_text("mutated", encoding="utf-8")

    result = verify(path)
    assert not result.ok
    assert any("input changed" in d for d in result.drifts)


def test_verify_detects_missing_input(tmp_path: Path):
    inp = tmp_path / "data.txt"
    inp.write_text("x", encoding="utf-8")
    rec = record(
        [sys.executable, "-c", "print('ok')"], cwd=tmp_path, inputs=[inp]
    )
    path = _save(rec, tmp_path / "rec.repro.yaml")

    inp.unlink()

    result = verify(path)
    assert not result.ok
    assert any("input missing" in d for d in result.drifts)


def test_verify_detects_exit_code_change(tmp_path: Path):
    # Record exit 0.
    rec = record([sys.executable, "-c", "print('a')"], cwd=tmp_path)
    # Mutate the recorded exit_code so the replay disagrees.
    rec["result"]["exit_code"] = 99
    path = _save(rec, tmp_path / "rec.repro.yaml")

    result = verify(path)
    assert not result.ok
    assert any("exit_code" in d for d in result.drifts)


def test_verify_raises_on_missing_record(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        verify(tmp_path / "nope.repro.yaml")


def test_verify_rejects_unknown_repro_version(tmp_path: Path):
    rec = record([sys.executable, "-c", "print('a')"], cwd=tmp_path)
    rec["repro_version"] = "999"
    path = _save(rec, tmp_path / "rec.repro.yaml")
    with pytest.raises(ValueError, match="repro_version"):
        verify(path)
