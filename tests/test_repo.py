# SPDX-License-Identifier: MIT
"""The repository itself must pass its own checks."""
import gen
import pr_status
import privacy_scan
import validate
from conftest import ROOT


def test_repository_validates():
    rep = validate.validate(ROOT)
    assert rep.errors == [], "\n".join(rep.errors)


def test_repository_privacy_scan_is_clean():
    findings = privacy_scan.scan(ROOT)
    assert findings == [], "\n".join(map(str, findings))


def test_generated_files_are_current():
    assert gen.main(["--root", str(ROOT), "--check"]) == 0


def test_status_json_matches_index():
    assert pr_status.main(["--root", str(ROOT), "--check"]) == 0
