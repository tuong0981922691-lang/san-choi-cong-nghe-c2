"""Tests for repro.recorder.record()."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from repro.recorder import record, write_record, INLINE_CAPTURE_LIMIT_BYTES


def test_record_simple_command_succeeds(tmp_path: Path):
    rec = record([sys.executable, "-c", "print('hi')"], cwd=tmp_path)
    assert rec["result"]["status"] == "ok"
    assert rec["result"]["exit_code"] == 0
    assert rec["result"]["stdout"]["bytes"] > 0
    # On Windows print adds \r\n, on Unix just \n — both are >= 3 bytes for "hi"
    assert "hi" in (rec["result"]["stdout"]["text"] or "")
    assert rec["repro_version"] == "1"


def test_record_failing_command_keeps_exit_code(tmp_path: Path):
    rec = record(
        [sys.executable, "-c", "import sys; sys.exit(7)"], cwd=tmp_path
    )
    assert rec["result"]["status"] == "error"
    assert rec["result"]["exit_code"] == 7


def test_record_missing_command(tmp_path: Path):
    rec = record(["__definitely_not_a_real_command_xyz__"], cwd=tmp_path)
    assert rec["result"]["status"] == "missing_command"
    assert rec["result"]["exit_code"] is None


def test_record_timeout(tmp_path: Path):
    rec = record(
        [sys.executable, "-c", "import time; time.sleep(5)"],
        cwd=tmp_path,
        timeout_s=1,
    )
    assert rec["result"]["status"] == "timeout"
    assert rec["result"]["exit_code"] is None


def test_record_hashes_declared_inputs(tmp_path: Path):
    inp = tmp_path / "data.txt"
    inp.write_text("hello world", encoding="utf-8")

    rec = record(
        [sys.executable, "-c", "print('ok')"],
        cwd=tmp_path,
        inputs=[inp],
    )
    assert len(rec["inputs"]) == 1
    entry = rec["inputs"][0]
    # path is relative to cwd
    assert entry["path"] == "data.txt"
    # sha256 of "hello world"
    assert entry["sha256"] == (
        "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
    )


def test_record_rejects_input_outside_cwd(tmp_path: Path):
    other_root = tmp_path.parent / (tmp_path.name + "_outside")
    other_root.mkdir()
    outside = other_root / "x.txt"
    outside.write_text("x", encoding="utf-8")
    with pytest.raises(ValueError, match="outside"):
        record([sys.executable, "-c", "pass"], cwd=tmp_path, inputs=[outside])


def test_record_rejects_invalid_capture(tmp_path: Path):
    with pytest.raises(ValueError, match="capture"):
        record([sys.executable, "-c", "pass"], cwd=tmp_path, capture="weird")


def test_record_hash_capture_mode_skips_text(tmp_path: Path):
    rec = record(
        [sys.executable, "-c", "print('hi')"],
        cwd=tmp_path,
        capture="hash",
    )
    assert rec["result"]["stdout"]["sha256"]
    assert rec["result"]["stdout"]["text"] is None


def test_record_inlines_short_output(tmp_path: Path):
    rec = record(
        [sys.executable, "-c", "print('short')"],
        cwd=tmp_path,
        capture="full",
    )
    assert rec["result"]["stdout"]["text"] is not None
    assert "short" in rec["result"]["stdout"]["text"]


def test_record_does_not_inline_huge_output(tmp_path: Path):
    # Produce output larger than INLINE_CAPTURE_LIMIT_BYTES (64 KiB).
    bytes_needed = INLINE_CAPTURE_LIMIT_BYTES + 1024
    rec = record(
        [
            sys.executable,
            "-c",
            f"import sys; sys.stdout.write('x' * {bytes_needed})",
        ],
        cwd=tmp_path,
        capture="full",
    )
    assert rec["result"]["stdout"]["bytes"] >= bytes_needed
    assert rec["result"]["stdout"]["text"] is None


def test_write_record_round_trips(tmp_path: Path):
    rec = record([sys.executable, "-c", "print('rt')"], cwd=tmp_path)
    out = tmp_path / "evidence" / "rt.repro.yaml"
    write_record(rec, out)
    assert out.exists()
    import yaml
    loaded = yaml.safe_load(out.read_text(encoding="utf-8"))
    assert loaded["repro_version"] == "1"
    assert loaded["result"]["exit_code"] == 0
