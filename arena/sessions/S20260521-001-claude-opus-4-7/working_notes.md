# Working Notes — S20260521-001

Bản ghi ngẫu nhiên trong quá trình làm việc. Không bắt buộc trung thực cấu trúc — đây là sổ tay.

---

## Câu hỏi đã cân nhắc và trả lời

**Q: Có cần signing crypto cho .repro.yaml không?**
A: Không. SHA-256 content hash là đủ ở scope S2. Crypto signing (sigstore/cosign) cần dependency lạ + key management → out of scope cho v1. Self_critique #1.

**Q: env_hash bắt được gì?**
A: Python version + platform + sys.path snapshot + sorted pip freeze (qua `pip freeze` subprocess). KHÔNG bắt env vars (PATH, LANG, etc.) — đó là weakness #5. v2 có thể mở rộng.

**Q: Replay command có thể có side effect không?**
A: Có. Đó là weakness lớn — verify path có thể trigger `rm -rf`, `git push`, etc. nếu .repro.yaml đã thoả thuận command nguy hiểm. Cần thêm dry-run mode + allowlist trong v2. Self_critique #4.

**Q: Working dir hash bắt được mọi file?**
A: KHÔNG. Chỉ hash các file mà user explicit declare via `--input` flag. Implicit dependencies (e.g. Python interpreter binary) không được bắt. Self_critique #7.

**Q: TimeoutExpired handling?**
A: Có. Default timeout = 300s. Nếu vượt, ghi `status: "timeout"` vào .repro.yaml + raise CLI exit code 124.

## Implementation sketch

```
repro/
  __init__.py     — version constants
  _hash.py        — SHA-256 helpers (file, stream, dict-canonical)
  _env.py         — environment fingerprint (python ver, pip freeze, OS)
  _git.py         — git HEAD + dirty flag (stdlib only — subprocess git)
  recorder.py     — record(command, inputs, timeout) → ReproRecord
  verifier.py     — verify(record_path) → VerifyResult (ok|drift|env_changed)
  auditor.py      — audit(evidence_dir) → AuditReport
  cli.py          — argparse, dispatch
```

## YAML schema for .repro.yaml

```yaml
repro_version: "1"
recorded_at: "2026-05-21T22:30:00Z"
command:
  argv: ["python", "scripts/c2_validate.py", "--strict"]
  cwd: "."
  timeout_s: 300
inputs:
  - path: "scripts/c2_validate.py"
    sha256: "abc...123"
  - path: "schemas/technology_manifest.schema.json"
    sha256: "def...456"
env:
  python_version: "3.12.10"
  platform: "Windows-10-..."
  pip_freeze_sha256: "789...000"
git:
  head: "ff0cd50"
  dirty: false
result:
  exit_code: 0
  duration_s: 0.42
  stdout_sha256: "111...222"
  stderr_sha256: "333...444"
  stdout: "(captured if --capture full, else null)"
  stderr: "(captured if --capture full, else null)"
  status: "ok"  # ok | error | timeout
```

Capture mode: `full` (inline stdout/stderr) vs `hash-only` (only sha256). Default: full for small outputs, fall back to hash-only > 64KB.

## CLI surface

```
repro record [--input PATH...] [--timeout SEC] [--output FILE] [--capture full|hash] -- COMMAND [ARGS...]
repro verify FILE.repro.yaml
repro audit DIR/
repro --version
```

## Tests planned

- test_recorder.py:
  - Record `echo hello` → check exit, stdout match
  - Record failing command → check exit_code preserved
  - Record with --input → check input hash in output
  - Record with timeout → check status=timeout
- test_verifier.py:
  - Verify deterministic command → ok
  - Verify with modified input file → drift
  - Verify with non-deterministic command (random) → drift
- test_auditor.py:
  - Audit dir with mixed runs → report
  - Audit dir with no records → empty report

Use `tmp_path` fixture for isolation.
