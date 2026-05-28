"""
repro — Reproducible Evidence Recorder for C2 Arena.

A small tool that turns the ad-hoc "evidence/" folder into a tamper-evident,
machine-verifiable record. Records a command together with its inputs, the
runtime environment, the git HEAD, and a hash of stdout/stderr. A verifier
can later replay the command and flag drift.
"""

REPRO_VERSION = "1"
SCHEMA_VERSION = "1"

__all__ = ["REPRO_VERSION", "SCHEMA_VERSION"]
