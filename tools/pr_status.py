#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""pr_status.py - refresh upstream/status.json from upstream/prs.yaml.

  python3 tools/pr_status.py              # fetch every PR's state with `gh api` (read-only GETs)
  python3 tools/pr_status.py --no-fetch   # offline: keep known entries, add missing ones as 'unknown', drop removed
  python3 tools/pr_status.py --check      # exit 1 if status.json does not list exactly the PRs in prs.yaml

For each PR it records: state (open, merged, closed), draft, title, url, updated_at, merged_at, merge_commit_sha,
head_sha and a review summary (approved, changes_requested, commented, none) from the latest review of each
reviewer. It needs the GitHub CLI (`gh`) for fetching; GH_TOKEN or the gh login provide read access to public PRs.
The output is sorted, so a refresh with no upstream change only moves 'fetched_at'.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import common  # noqa: E402


def gh_get(path, runner=subprocess.run):
    """GET https://api.github.com/<path> through `gh api` and return the decoded JSON."""
    r = runner(["gh", "api", "-X", "GET", "-H", "Accept: application/vnd.github+json", path],
               capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"gh api {path}: {r.stderr.strip() or r.stdout.strip()}")
    return json.loads(r.stdout)


def review_summary(reviews):
    latest = {}
    for rv in reviews or []:
        user = (rv.get("user") or {}).get("login")
        state = rv.get("state")
        if user and state in ("APPROVED", "CHANGES_REQUESTED", "COMMENTED", "DISMISSED"):
            if state == "COMMENTED" and latest.get(user) in ("APPROVED", "CHANGES_REQUESTED"):
                continue
            latest[user] = state
    vals = set(latest.values())
    if "CHANGES_REQUESTED" in vals:
        return "changes_requested"
    if "APPROVED" in vals:
        return "approved"
    if "COMMENTED" in vals:
        return "commented"
    return "none"


def fetch_one(repo, number, get=gh_get):
    pr = get(f"repos/{repo}/pulls/{number}")
    try:
        reviews = get(f"repos/{repo}/pulls/{number}/reviews?per_page=100")
    except RuntimeError:
        reviews = []
    state = "merged" if pr.get("merged_at") else pr.get("state", "unknown")
    return {
        "state": state,
        "draft": bool(pr.get("draft")),
        "title": pr.get("title"),
        "url": pr.get("html_url") or f"https://github.com/{repo}/pull/{number}",
        "updated_at": pr.get("updated_at"),
        "merged_at": pr.get("merged_at"),
        "merge_commit_sha": pr.get("merge_commit_sha") if pr.get("merged_at") else None,
        "head_sha": (pr.get("head") or {}).get("sha"),
        "review": review_summary(reviews),
    }


def unknown_entry(repo, number, title=None):
    return {"state": "unknown", "draft": False, "title": title, "url": f"https://github.com/{repo}/pull/{number}",
            "updated_at": None, "merged_at": None, "merge_commit_sha": None, "head_sha": None, "review": "none"}


def refresh(root, fetch=True, get=gh_get, now=None):
    root = pathlib.Path(root)
    prs = common.load_prs(root).get("prs") or []
    old = common.load_status(root) if (root / "upstream" / "status.json").exists() else {}
    old_prs = old.get("prs", {}) if isinstance(old, dict) else {}
    out, failures = {}, []
    for pr in prs:
        key = common.pr_key(pr["repo"], pr["number"])
        if fetch:
            try:
                out[key] = fetch_one(pr["repo"], pr["number"], get)
                continue
            except (RuntimeError, json.JSONDecodeError, OSError) as e:
                failures.append(f"{key}: {e}")
        out[key] = old_prs.get(key) or unknown_entry(pr["repo"], pr["number"], pr.get("title"))
    doc = {
        "generated_by": "tools/pr_status.py",
        "source": "upstream/prs.yaml",
        "fetched_at": (now or dt.datetime.now(dt.timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ") if fetch and not failures
        else old.get("fetched_at"),
        "prs": dict(sorted(out.items())),
    }
    return doc, failures


def write(root, doc):
    p = pathlib.Path(root) / "upstream" / "status.json"
    p.write_text(json.dumps(doc, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=str(common.ROOT))
    ap.add_argument("--no-fetch", action="store_true", help="do not call the network; reconcile with prs.yaml only")
    ap.add_argument("--check", action="store_true", help="exit 1 if status.json and prs.yaml list different PRs")
    a = ap.parse_args(argv)
    root = pathlib.Path(a.root)
    if a.check:
        want = {common.pr_key(p["repo"], p["number"]) for p in common.load_prs(root).get("prs") or []}
        have = set(common.load_status(root).get("prs", {}))
        for k in sorted(want - have):
            print(f"missing from status.json: {k}")
        for k in sorted(have - want):
            print(f"not in prs.yaml: {k}")
        return 1 if want != have else 0
    doc, failures = refresh(root, fetch=not a.no_fetch)
    write(root, doc)
    for f in failures:
        print(f"WARN  {f}", file=sys.stderr)
    states = {}
    for v in doc["prs"].values():
        states[v["state"]] = states.get(v["state"], 0) + 1
    print(f"pr_status: {len(doc['prs'])} PR(s): " + ", ".join(f"{k} {n}" for k, n in sorted(states.items())))
    return 1 if failures and not a.no_fetch else 0


if __name__ == "__main__":
    sys.exit(main())
