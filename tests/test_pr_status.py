# SPDX-License-Identifier: MIT
import datetime as dt
import json

import pr_status


def fake_get(path):
    if path.endswith("/reviews?per_page=100"):
        return [{"user": {"login": "a"}, "state": "COMMENTED"}, {"user": {"login": "a"}, "state": "APPROVED"}]
    return {"state": "closed", "merged_at": "2026-11-06T00:00:00Z", "merge_commit_sha": "abc", "draft": False,
            "title": "Example change", "html_url": "https://github.com/example/linux/pull/1",
            "updated_at": "2026-11-06T00:00:00Z", "head": {"sha": "def"}}


def test_fetch_records_merged_state(mini_repo):
    now = dt.datetime(2026, 11, 7, 12, 0, tzinfo=dt.timezone.utc)
    doc, failures = pr_status.refresh(mini_repo, fetch=True, get=fake_get, now=now)
    assert failures == []
    e = doc["prs"]["example/linux#1"]
    assert e["state"] == "merged" and e["review"] == "approved" and e["merge_commit_sha"] == "abc"
    assert doc["fetched_at"] == "2026-11-07T12:00:00Z"


def test_no_fetch_keeps_known_and_adds_unknown(mini_repo):
    (mini_repo / "upstream" / "prs.yaml").write_text(
        (mini_repo / "upstream" / "prs.yaml").read_text() +
        "  - repo: example/m1n1\n    number: 7\n    title: Loader change\n    machines: [J999t]\n    features: []\n")
    doc, _ = pr_status.refresh(mini_repo, fetch=False)
    assert doc["prs"]["example/linux#1"]["state"] == "open"
    assert doc["prs"]["example/m1n1#7"]["state"] == "unknown"
    assert doc["fetched_at"] == "2026-11-05T00:00:00Z"
    pr_status.write(mini_repo, doc)
    assert pr_status.main(["--root", str(mini_repo), "--check"]) == 0


def test_fetch_failure_falls_back(mini_repo):
    def broken(path):
        raise RuntimeError("offline")
    doc, failures = pr_status.refresh(mini_repo, fetch=True, get=broken)
    assert failures and doc["prs"]["example/linux#1"]["state"] == "open"
    assert doc["fetched_at"] == "2026-11-05T00:00:00Z"


def test_review_summary():
    assert pr_status.review_summary([]) == "none"
    assert pr_status.review_summary([{"user": {"login": "x"}, "state": "CHANGES_REQUESTED"},
                                     {"user": {"login": "y"}, "state": "APPROVED"}]) == "changes_requested"
