# SPDX-License-Identifier: MIT
import pathlib
import shutil
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
FIX = pathlib.Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(ROOT / "tools"))


@pytest.fixture
def mini_repo(tmp_path):
    """A small, valid tracker tree: one fictional board (J999t) with results, a build, a PR index and a topic."""
    root = tmp_path / "repo"
    shutil.copytree(FIX / "mini", root)
    shutil.copytree(ROOT / "schema", root / "schema")
    shutil.copy(FIX / "machine-valid.yaml", root / "machines" / "j999t" / "machine.yaml")
    return root
