# AGENTS.md

## Cursor Cloud specific instructions

This is a Python validation-and-governance repository (no running servers or databases). The development "application" is a set of Python scripts and pytest tests.

### Quick reference

- **Language:** Python 3.9+ (system has 3.12)
- **Dependencies:** `pip install -r scripts/requirements.txt` (pyyaml, jsonschema, pytest)
- **Lint/validate:** `python3 scripts/c2_validate.py --strict`
- **Score check:** `python3 scripts/c2_score_check.py`
- **Secret scan:** `python3 scripts/c2_secret_scan.py`
- **Parse check:** `python3 scripts/c2_parse_check.py`
- **Tests:** `python3 -m pytest tests/ -v`
- **Scaffold new tech:** `python3 scripts/c2_new_tech.py --slug <name> --domain <domain> --mode NEW_FROM_WASTE`
- **Rebuild indexes:** `python3 scripts/c2_index.py --rebuild`

### Non-obvious notes

- `pytest` and `jsonschema` CLI are installed to `~/.local/bin`; ensure `PATH` includes it (`export PATH="$HOME/.local/bin:$PATH"`).
- Some tests in `test_score_rules.py` and `test_manifest_rules.py` are parametrized over vault contents. They show as SKIPPED when `vault/technologies/` is empty — this is expected.
- The CI workflow (`validate-submission.yml`) runs: validate --strict, score_check, secret_scan, then pytest. Replicate this locally before opening PRs.
- No web server, database, or Docker is required for development.
- All validation scripts exit 0 on success and non-zero on failure; treat exit code as the pass/fail signal.
