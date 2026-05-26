# AGENTS.md

## Cursor Cloud specific instructions

This is a Python-based validation/testing framework (no web server, no database, no Docker required). All "services" are CLI scripts and pytest tests.

### Quick reference

| Task | Command |
|------|---------|
| Install deps | `pip install -r scripts/requirements.txt` |
| Full validation | `python scripts/c2_validate.py --strict` |
| Score check | `python scripts/c2_score_check.py` |
| Secret scan | `python scripts/c2_secret_scan.py` |
| Run tests | `python -m pytest tests/ -v` |
| Scaffold tech | `python scripts/c2_new_tech.py --slug <name> --domain <domain>` |
| Scaffold challenge | `python scripts/c2_new_challenge.py --target <TECH_ID> --delta <float>` |
| Rebuild indexes | `python scripts/c2_index.py --rebuild` |

### Non-obvious notes

- `pip install` defaults to `--user` in this environment; ensure `$HOME/.local/bin` is on `PATH` so `pytest` CLI is available (or invoke via `python -m pytest`).
- The vault starts empty. Manifest/score tests are parameterized over vault contents, so they show as SKIPPED when the vault has no technologies yet. This is normal.
- `c2_validate.py --strict` is the most comprehensive single check — it covers structure, schemas, scores, and secret scanning in one pass.
- All validation scripts must be run from the repo root (`/workspace`).
- See `README.md` sections 17 and 23 for full script usage and test details.
