"""The tabbed web view works offline — checked in jsdom, driven from pytest.

Runs tests/web/check_page.mjs, which loads the committed web/index.html (and its
data/*.js globals) from file:// URLs in jsdom and asserts the hash-driven tabs:
default tab with no hash, deep links (#gate, #classify), unknown-hash fallback,
click/hashchange/back-button switching, and that all three tabs' content renders.

Hermetic at run time (no network), but it needs Node plus the jsdom devDependency
(npm ci --prefix tests/web). When either is missing the test SKIPS rather than
fails, so the Python-only suite stays green without a JS toolchain; CI installs
both so the checks actually gate merges.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
HARNESS = ROOT / "tests" / "web" / "check_page.mjs"
JSDOM_DIR = ROOT / "tests" / "web" / "node_modules" / "jsdom"


def test_web_view_tabs_via_jsdom():
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not installed")
    if not JSDOM_DIR.exists():
        pytest.skip("jsdom is not installed (run: npm ci --prefix tests/web)")
    proc = subprocess.run(
        [node, str(HARNESS)],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=ROOT,
    )
    assert (
        proc.returncode == 0
    ), f"jsdom web view checks failed:\n{proc.stdout}\n{proc.stderr}"
