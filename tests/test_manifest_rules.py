"""
C2 Arena — Manifest Rules Tests
Kiểm tra schema và luật cơ bản của mọi technology manifest.
"""

import json
import yaml
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
TECH_DIR = REPO_ROOT / "vault" / "technologies"

REQUIRED_FIELDS = ["id", "slug", "title", "version", "status", "mode", "creator", "domain", "safety", "score", "claims"]
VALID_MODES = ["NEW_FROM_WASTE", "UPGRADE_EXISTING"]
VALID_DOMAINS = [
    "algorithm", "ai-tooling", "developer-tool", "data-system",
    "simulation", "security-defense", "creative-media-safe",
    "education", "automation-safe", "architecture-pattern"
]
VALID_STATUSES = ["proposed", "accepted", "superseded", "retired", "rejected"]


def get_all_manifests():
    manifests = []
    if not TECH_DIR.is_dir():
        return manifests
    for tech_dir in TECH_DIR.iterdir():
        if not tech_dir.is_dir():
            continue
        versions = tech_dir / "versions"
        if not versions.is_dir():
            continue
        for v in versions.iterdir():
            m = v / "manifest.yaml"
            if m.exists():
                manifests.append((tech_dir.name, v.name, m))
    return manifests


@pytest.mark.parametrize("tech_name,version,manifest_path", get_all_manifests())
def test_required_fields_present(tech_name, version, manifest_path):
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    for field in REQUIRED_FIELDS:
        assert field in data, f"{tech_name}/{version}: missing required field '{field}'"


@pytest.mark.parametrize("tech_name,version,manifest_path", get_all_manifests())
def test_valid_mode(tech_name, version, manifest_path):
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    mode = data.get("mode")
    assert mode in VALID_MODES, f"{tech_name}/{version}: invalid mode '{mode}'"


@pytest.mark.parametrize("tech_name,version,manifest_path", get_all_manifests())
def test_valid_domain(tech_name, version, manifest_path):
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    primary = data.get("domain", {}).get("primary")
    assert primary in VALID_DOMAINS, f"{tech_name}/{version}: invalid domain '{primary}'"


@pytest.mark.parametrize("tech_name,version,manifest_path", get_all_manifests())
def test_valid_status(tech_name, version, manifest_path):
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    status = data.get("status")
    assert status in VALID_STATUSES, f"{tech_name}/{version}: invalid status '{status}'"
