"""
C2 Arena — Repo Integrity Tests
Kiểm tra cấu trúc cơ bản của kho.
"""

import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

REQUIRED_ROOT_FILES = [
    "README.md",
    "AGENT_START_HERE.md",
    "C2_CHARTER.md",
    "C2_PHILOSOPHY.md",
    "C2_LAWS.md",
    "ARENA_PROTOCOL.md",
    "SCORE_RULES.md",
    "SECURITY.md",
    "SAFETY_BOUNDARIES.md",
    "GOVERNANCE.md",
    ".gitignore",
]

REQUIRED_DIRS = [
    "waste",
    "arena",
    "vault/technologies",
    "vault/challenges",
    "vault/crowns",
    "templates/technology",
    "templates/challenge",
    "templates/session",
    "schemas",
    "scripts",
    "docs",
    "proposals",
    "reports",
]

REQUIRED_SCRIPTS = [
    "scripts/c2_validate.py",
    "scripts/c2_score_check.py",
    "scripts/c2_new_tech.py",
    "scripts/c2_new_challenge.py",
    "scripts/c2_index.py",
    "scripts/c2_secret_scan.py",
    "scripts/safe_run.sh",
]

REQUIRED_SCHEMAS = [
    "schemas/technology_manifest.schema.json",
    "schemas/challenge_manifest.schema.json",
    "schemas/waste_item.schema.json",
    "schemas/scorecard.schema.json",
    "schemas/session_manifest.schema.json",
]


@pytest.mark.parametrize("filename", REQUIRED_ROOT_FILES)
def test_root_file_exists(filename):
    assert (REPO_ROOT / filename).exists(), f"Missing required root file: {filename}"


@pytest.mark.parametrize("dirname", REQUIRED_DIRS)
def test_required_dir_exists(dirname):
    assert (REPO_ROOT / dirname).is_dir(), f"Missing required directory: {dirname}"


@pytest.mark.parametrize("script", REQUIRED_SCRIPTS)
def test_script_exists(script):
    assert (REPO_ROOT / script).exists(), f"Missing script: {script}"


@pytest.mark.parametrize("schema", REQUIRED_SCHEMAS)
def test_schema_exists(schema):
    assert (REPO_ROOT / schema).exists(), f"Missing schema: {schema}"


def test_waste_index_exists():
    assert (REPO_ROOT / "waste" / "index.yaml").exists()


def test_crown_registry_exists():
    assert (REPO_ROOT / "vault" / "crowns" / "CROWN_REGISTRY.yaml").exists()


def test_leaderboard_exists():
    assert (REPO_ROOT / "vault" / "crowns" / "LEADERBOARD.md").exists()


def test_gitignore_has_env():
    gi = REPO_ROOT / ".gitignore"
    content = gi.read_text(encoding="utf-8")
    assert ".env" in content, ".gitignore must contain .env"
    assert "*.key" in content, ".gitignore must contain *.key"


def test_codeowners_exists():
    assert (REPO_ROOT / ".github" / "CODEOWNERS").exists()


def test_workflows_exist():
    assert (REPO_ROOT / ".github" / "workflows" / "validate-submission.yml").exists()
    assert (REPO_ROOT / ".github" / "workflows" / "repo-integrity.yml").exists()
