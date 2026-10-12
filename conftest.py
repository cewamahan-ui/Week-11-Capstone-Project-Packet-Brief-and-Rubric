"""Root conftest: puts the repository root on sys.path.

This is what lets every test import the package as ``src.afyaplus.*``
regardless of how pytest is invoked (repo root or a subdirectory).
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
