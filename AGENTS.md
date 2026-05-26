# AGENTS.md

## Cursor Cloud specific instructions

This is a Python-based repository governance framework (no web server or runtime services). The "application" consists of Python validation scripts and a pytest test suite.

### Quick reference

- **Language:** Python 3.12
- **Dependencies:** `pip install -r scripts/requirements.txt` (pyyaml, jsonschema, pytest)
- **Lint/Validate:** `python scripts/c2_validate.py --strict`
- **Score check:** `python scripts/c2_score_check.py`
- **Secret scan:** `python scripts/c2_secret_scan.py`
- **Parse check:** `python scripts/c2_parse_check.py`
- **Tests:** `python -m pytest tests/ -v`
- **Scaffold new tech:** `python scripts/c2_new_tech.py --slug <name> --domain <domain> --mode NEW_FROM_WASTE`
- **Rebuild indexes:** `python scripts/c2_index.py --rebuild`

### Non-obvious notes

- PATH must include `$HOME/.local/bin` for user-installed pytest/jsonschema CLI to be found. The pip packages install there because site-packages is not writable.
- The vault is empty in a fresh repo — tests that parametrize over vault manifests will show as SKIPPED (not failures).
- `c2_index.py` requires the `--rebuild` flag to actually rebuild indexes (no-arg shows usage).
- There is no web server, database, or Docker requirement for normal development. Docker is only needed for `safe_run.sh` (optional sandboxed code execution).
- The CI workflow (`.github/workflows/validate-submission.yml`) runs the same validation commands listed above — matching those locally ensures PR checks pass.
