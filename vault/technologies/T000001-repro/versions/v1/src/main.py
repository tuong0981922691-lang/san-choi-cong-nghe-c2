"""Entrypoint that lets the tool be invoked as ``python src/main.py``."""

from __future__ import annotations

import sys
from pathlib import Path

# Allow ``python src/main.py …`` from the technology root by adding the
# parent of this file (``src/``) to sys.path so ``repro`` is importable.
_SRC_DIR = Path(__file__).resolve().parent
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from repro.cli import main  # noqa: E402  (intentional after sys.path tweak)


if __name__ == "__main__":
    raise SystemExit(main())
