# Architecture

## 1. Module boundary

```
src/
└── repro/
    ├── __init__.py    — REPRO_VERSION, SCHEMA_VERSION constants
    ├── cli.py         — argparse entry point, subcommand dispatch (~150 LOC)
    ├── recorder.py    — record() → dict, write_record() → file (~150 LOC)
    ├── verifier.py    — verify() → VerifyResult (~80 LOC)
    ├── auditor.py     — audit() → AuditReport (~100 LOC)
    ├── _hash.py       — file/text/canonical SHA-256 helpers (~30 LOC)
    ├── _env.py        — collect_env(): Python + platform + pip-freeze hash (~40 LOC)
    └── _git.py        — collect_git(): HEAD + dirty flag, optional (~40 LOC)
src/main.py            — thin shim so `python src/main.py` works from anywhere
```

Internal modules (`_hash`, `_env`, `_git`) are leading-underscore to signal "internal API, may change without notice." The public API is `recorder.record`, `recorder.write_record`, `verifier.verify`, `auditor.audit`, and the CLI.

## 2. Data model

### `.repro.yaml` (output of `record`, input of `verify`/`audit`)

```yaml
repro_version: "1"
schema_version: "1"
recorded_at: "<ISO 8601 UTC>"
command:
  argv: [str, …]          # always a list — no shell, no string splitting
  cwd: str                 # working dir (relative if same as caller cwd)
  timeout_s: int           # hard wall-clock cap
  capture: "full" | "hash"
inputs:                    # caller-declared files the cmd depends on
  - path: str              # relative to cwd
    sha256: str            # 64-char hex
env:
  python:
    implementation: str
    version: str
    executable: str
  platform: str            # platform.platform() output
  pip_freeze_sha256: str | null
git:
  head: str | null         # full HEAD sha if in a git repo, else null
  dirty: bool | null       # true if tracked files modified
result:
  status: "ok" | "error" | "timeout" | "missing_command"
  exit_code: int | null
  duration_s: float
  stdout:
    sha256: str
    bytes: int
    text: str | null       # inlined only if capture=full AND bytes ≤ 64KiB
  stderr: { same shape as stdout }
```

### `VerifyResult` / `AuditReport`

Plain dataclasses with `.to_dict()` so they round-trip through JSON or YAML cleanly. No custom serializers needed.

## 3. Control flow

### `record(argv, cwd, inputs, timeout_s, capture)`

```
validate capture in {"full","hash"}        ← raise ValueError early
resolve cwd to absolute path
for each input p in inputs:                ← FAIL FAST
    resolve to absolute path
    enforce: p must be under cwd           ← refuse path traversal
    enforce: p must exist + be a regular file
    sha256(p) → inputs_block
collect env + git (best-effort, may be null)
spawn subprocess.run(argv, stdout=PIPE, stderr=PIPE, timeout=timeout_s)
catch TimeoutExpired   → status="timeout", stdout/stderr from exception
catch FileNotFoundError → status="missing_command"
else                    → status="ok" if exit_code==0 else "error"
hash stdout/stderr
return record dict
```

Notes on safety:
- `argv` is always a list. Never `shell=True`. The subprocess invocation does NOT interpret shell metacharacters.
- `cwd` is resolved before subprocess spawns. Subprocess inherits it.
- No `check=True` — we capture failing exit codes intentionally; we don't want a tool that records exit-7 to itself fail with `CalledProcessError`.

### `verify(record_path, cwd=None)`

```
parse .repro.yaml
validate repro_version == "1"                       ← raise ValueError if not
re-hash each declared input
if any input drift → return early, do NOT replay   ← refuse unsafe replay
re-run record() with same argv, cwd, timeout, capture
compare: status, exit_code, stdout.sha256, stderr.sha256
return VerifyResult(ok=no_drift, drifts=[…])
```

Early-return on input drift is deliberate: if the source you're verifying against has already changed, replaying gives a misleading "command output changed" message when the real issue is "source changed." Surface the right diagnosis.

### `audit(directory)`

```
walk directory.rglob("*.repro.yaml")
for each file:
    parse YAML safely (yaml.safe_load)
    if parse fails → status="schema_invalid"
    if repro_version mismatch → add issue
    if git.dirty == true → add issue + increment dirty_git_count
    bucket into status counters
return AuditReport(total, ok_count, error_count, …, entries=[…])
```

`audit` never spawns subprocess. It is a read-only scan, safe to run on untrusted records.

## 4. Determinism design

The tool itself must be deterministic except where the inputs make it non-deterministic. Specifically:
- The YAML key order is preserved (`yaml.safe_dump(sort_keys=False)`) so the diff between two records of "the same" command shows only meaningful differences.
- Floats (duration) are rounded to 4 decimals to dampen monotonic-clock jitter.
- Timestamps are UTC ISO 8601 with second-resolution to avoid sub-second clock jitter.
- All hashes are SHA-256 hex lowercase (RFC 4648 §8 alphabet).

## 5. Failure modes (mapped to status)

| Status | When | Recovery |
|---|---|---|
| `ok` | exit 0 | record committed |
| `error` | exit ≠ 0 | record committed; reviewer reads exit_code |
| `timeout` | wall clock exceeded `timeout_s` | record committed; reviewer increases timeout or fixes hang |
| `missing_command` | argv[0] not found | record committed with empty stdout; reviewer fixes PATH |
| (`record()` raises) | bad input declaration, bad cwd, bad capture | CLI prints to stderr, exits 2; no record written |

## 6. Trust boundary

```
+----------------------+      +-------------------+      +-----------------+
| caller (CI, AI agent)| ---> | repro CLI/library | ---> | subprocess.run  |
|  — controls argv     |      |  — pure functions |      |  — runs argv    |
|  — controls inputs[] |      |  — no globals      |      |  — captures I/O |
+----------------------+      +-------------------+      +-----------------+
                                       |
                                       v
                              +-----------------+
                              | .repro.yaml file|
                              | (committed)     |
                              +-----------------+
```

The tool itself owns no secrets, opens no network sockets, and writes no files outside the explicit `--output` path. All trust flows from caller → tool → subprocess. The tool is faithful courier; it cannot vet what the caller wants to run.

## 7. Performance

| Operation | Big-O | Wall time on a typical C2 validator run |
|---|---|---|
| record() with no inputs | O(stdout+stderr size) | ~50–500 ms overhead over the command itself |
| record() with 5 small inputs | O(input size + output size) | ~+5 ms per input file |
| verify() | 2× record cost (re-hash + replay) | ~2× |
| audit(dir) | O(total bytes of all .repro.yaml files) | ~10 ms per record |

Not optimized for thousands of records — but the C2 use case is dozens per technology, hundreds across the whole vault. Adequate.
