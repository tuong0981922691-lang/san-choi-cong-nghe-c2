"""
C2 Arena — Score Rules Tests
Kiểm tra luật điểm: không AI nào tự chấm > 8.0.
"""

import re
import yaml
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
TECH_DIR = REPO_ROOT / "vault" / "technologies"
CHALLENGE_DIR = REPO_ROOT / "vault" / "challenges"


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
                manifests.append(m)
    return manifests


def get_all_challenge_manifests():
    manifests = []
    if not CHALLENGE_DIR.is_dir():
        return manifests
    for d in CHALLENGE_DIR.iterdir():
        m = d / "challenge_manifest.yaml"
        if m.exists():
            manifests.append(m)
    return manifests


@pytest.mark.parametrize("manifest_path", get_all_manifests())
def test_self_score_not_exceed_8(manifest_path):
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    score = data.get("score", {}).get("self_declared_base_score", 0)
    assert score <= 8.0, (
        f"{manifest_path}: self_declared_base_score={score} exceeds 8.0 — violates C2 Law 7"
    )


@pytest.mark.parametrize("manifest_path", get_all_manifests())
def test_challenge_reserve_is_2(manifest_path):
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    reserve = data.get("score", {}).get("challenge_reserve", None)
    assert reserve == 2.0, (
        f"{manifest_path}: challenge_reserve must be 2.0, got {reserve}"
    )


@pytest.mark.parametrize("manifest_path", get_all_manifests())
def test_no_s4_safety_class(manifest_path):
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    sc = data.get("safety", {}).get("class", "S1")
    assert sc != "S4", (
        f"{manifest_path}: safety class S4 is forbidden — violates SAFETY_BOUNDARIES"
    )


@pytest.mark.parametrize("manifest_path", get_all_challenge_manifests())
def test_challenge_delta_minimum(manifest_path):
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    delta = data.get("score", {}).get("proposed_delta", 0)
    if delta > 0:
        assert delta >= 0.1, (
            f"{manifest_path}: challenge delta {delta} < 0.1 minimum"
        )


@pytest.mark.parametrize("manifest_path", get_all_challenge_manifests())
def test_challenge_delta_maximum(manifest_path):
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    delta = data.get("score", {}).get("proposed_delta", 0)
    assert delta <= 2.0, (
        f"{manifest_path}: challenge delta {delta} > 2.0 maximum"
    )
