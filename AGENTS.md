# AGENTS.md

## Cursor Cloud specific instructions

### Overview

This is a **Python-based governance/validation framework** ("C2 Arena") — not a web application. There is no server to start, no database, and no external API dependencies. The "application" consists of Python validation scripts, JSON schemas, and a pytest test suite.

### Running tests and validators

All commands documented in the `scripts/README.md` and `README.md` (section 17) are the canonical references. Key commands:

```bash
python3 -m pytest tests/ -v                   # Full test suite (42 pass, 9 skip when vault is empty)
python3 scripts/c2_validate.py --strict        # Strict repo structure validation
python3 scripts/c2_score_check.py              # Score rule enforcement
python3 scripts/c2_secret_scan.py              # Secret leak scanner
python3 scripts/c2_parse_check.py              # YAML/JSON parse validation
python3 scripts/c2_index.py --rebuild          # Rebuild vault indexes and leaderboard
```

### Scaffolding new technologies

```bash
python3 scripts/c2_new_tech.py --slug <name> --domain <domain> --mode NEW_FROM_WASTE
```

This creates a full technology directory under `vault/technologies/` with all 13 required files from templates.

### Gotchas

- `pytest` and other pip-installed scripts land in `~/.local/bin` which may not be on `PATH`. Either use `python3 -m pytest` or ensure `~/.local/bin` is on `PATH`.
- The 9 skipped tests in pytest are expected — they are parameterized tests that only run when technologies/challenges exist in `vault/`. They become active once submissions are added.
- Docker is only needed for `scripts/safe_run.sh` (sandbox execution of submitted code). All other scripts work without Docker.
- The CI workflow uses Python 3.11, but the codebase works with Python 3.9+ (Python 3.12 verified locally).
