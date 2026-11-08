#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""validate.py - check the tracker's data against the schemas and the evidence rules.

  python3 tools/validate.py                      # whole repository; exit 1 on any error
  python3 tools/validate.py --stale-report DIR   # also write DIR/<board>.md for boards with stale cells
  python3 tools/validate.py --today 2026-12-31   # evaluate staleness as of another date
  python3 tools/validate.py --strict             # warnings count as errors

Rules (README, "States and evidence"):
  * every machine.yaml, build recipe, result front matter and prs.yaml matches its schema;
  * feature ids exist in schema/features.yaml, setup ids exist in the machine file;
  * works-* needs kind native and a result file in machines/<board>/results/ that exists, whose anchor exists, and
    whose front matter has a date, the same board and kind native; 'verified' is the date of the newest such result;
    works-daily also needs the setup's current_build recipe;
  * kind reported only with state reported; state reported needs a link; drafts hold no native cells;
  * attended needs a note and a link, prepared a link or an upstream PR, blocked a result or issue link,
    not-realistic a note;
  * every local evidence link resolves (file and anchor), every upstream ref is listed in upstream/prs.yaml;
  * a works-* cell whose 'verified' date is more than 30 days old is stale (a warning).
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import common  # noqa: E402
from common import WORKS  # noqa: E402

CLOCK_SKEW_DAYS = 1   # a result dated 'tomorrow' in UTC is accepted (time zones)


class Report:
    def __init__(self):
        self.errors, self.warnings = [], []
        self.stale = {}   # board -> [(feature, setup, verified, state)]

    def err(self, where, msg):
        self.errors.append(f"{where}: {msg}")

    def warn(self, where, msg):
        self.warnings.append(f"{where}: {msg}")


def _rel(root, p):
    try:
        return str(pathlib.Path(p).resolve().relative_to(root.resolve()))
    except ValueError:
        return str(p)


def check_result_file(root, rep, path, board, setups, feature_ids, today, cache):
    """Validate one result file; returns its front matter (or None). Cached per path."""
    key = str(path.resolve())
    if key in cache:
        return cache[key]
    where = _rel(root, path)
    text = path.read_text(encoding="utf-8")
    fm, body = common.front_matter(text)
    cache[key] = None
    if fm is None:
        rep.err(where, "no front matter (--- ... --- block at the top)")
        return None
    for e in common.schema_errors(fm, common.load_schema("result.schema.json")):
        rep.err(where, e)
    if fm.get("board") != board:
        rep.err(where, f"front matter board {fm.get('board')!r} is not {board!r}")
    if setups is not None and fm.get("setup") not in setups:
        rep.err(where, f"setup {fm.get('setup')!r} is not a setup of {board}")
    for f in fm.get("features", []) or []:
        if f not in feature_ids:
            rep.err(where, f"unknown feature id {f!r}")
    d = common.parse_date(fm.get("date"))
    m = re.match(r"^(\d{4}-\d{2}-\d{2})-", path.name)
    if d is None:
        rep.err(where, "front matter date missing or unparsable")
    else:
        if m and m.group(1) != d.isoformat():
            rep.err(where, f"file name date {m.group(1)} differs from front matter date {d.isoformat()}")
        if (d - today).days > CLOCK_SKEW_DAYS:
            rep.err(where, f"date {d.isoformat()} is in the future")
    if "payload_sha256" not in fm and "payload_sha256_prefix" not in fm and "payload" not in fm:
        rep.warn(where, "no payload, payload_sha256 or payload_sha256_prefix in the front matter")
    cache[key] = (fm, body)
    return cache[key]


def resolve_evidence(root, machine_dir, ev):
    """-> (path, anchor) for a local evidence link, or (None, None) for a URL."""
    if ev.startswith("https://"):
        return None, None
    target, _, anchor = ev.partition("#")
    return (machine_dir / target), (anchor or None)


def validate(root=common.ROOT, today=None, rep=None):
    root = pathlib.Path(root)
    today = today or common.today()
    rep = rep or Report()
    fpath = root / "schema" / "features.yaml"
    feats = common.load_yaml(fpath if fpath.exists() else common.ROOT / "schema" / "features.yaml")
    feature_ids = set(feats["features"])
    machine_schema = common.load_schema("machine.schema.json")
    build_schema = common.load_schema("build.schema.json")
    prs_schema = common.load_schema("prs.schema.json")

    # ---- upstream index
    prs_doc = common.load_prs(root)
    for e in common.schema_errors(prs_doc, prs_schema):
        rep.err("upstream/prs.yaml", e)
    pr_keys = set()
    for i, pr in enumerate(prs_doc.get("prs", []) or []):
        k = common.pr_key(pr.get("repo"), pr.get("number"))
        if k in pr_keys:
            rep.err("upstream/prs.yaml", f"duplicate entry {k}")
        pr_keys.add(k)
        for f in pr.get("features", []) or []:
            if f not in feature_ids:
                rep.err("upstream/prs.yaml", f"{k}: unknown feature id {f!r}")
        for s in pr.get("stacked_on", []) or []:
            if s not in pr_keys and s not in {common.pr_key(p.get("repo"), p.get("number")) for p in prs_doc["prs"]}:
                rep.warn("upstream/prs.yaml", f"{k}: stacked on {s}, which is not in the index")

    boards = {}
    cache = {}
    # ---- machines
    for mf, m in common.load_machines(root):
        where = _rel(root, mf)
        if not isinstance(m, dict):
            rep.err(where, "not a mapping")
            continue
        errs = common.schema_errors(m, machine_schema)
        for e in errs:
            rep.err(where, e)
        board = m.get("board")
        if not isinstance(board, str):
            continue
        if mf.parent.name != board.lower():
            rep.err(where, f"directory {mf.parent.name!r} must be the lower-case board id {board.lower()!r}")
        boards[board] = m
        setups = {}
        for s in m.get("setups", []) or []:
            if s.get("id") in setups:
                rep.err(where, f"duplicate setup id {s.get('id')!r}")
            setups[s.get("id")] = s
            cb = s.get("current_build")
            if cb and not (root / cb).exists():
                rep.err(where, f"setup {s.get('id')}: current_build {cb} does not exist")
        draft = bool(m.get("draft"))
        for fid, cells in (m.get("features") or {}).items():
            if fid not in feature_ids:
                rep.err(where, f"unknown feature id {fid!r} (see schema/features.yaml)")
            if not isinstance(cells, list):
                continue
            for ci, c in enumerate(cells):
                if not isinstance(c, dict):
                    continue
                cw = f"{where}: {fid}[{ci}]"
                check_cell(root, rep, cw, mf.parent, board, c, setups, draft, feature_ids, pr_keys, today, cache)
                if common.is_stale(c, today):
                    rep.stale.setdefault(board, []).append((fid, c.get("setup"), c.get("verified"), c.get("state")))
                    rep.warn(cw, f"stale: {c.get('state')} last verified {c.get('verified')} "
                                 f"(more than {common.STALE_DAYS} days before {today.isoformat()})")

        # every result file of the board, cited or not
        rdir = mf.parent / "results"
        if rdir.is_dir():
            for rf in sorted(rdir.glob("*.md")):
                if not re.match(r"^\d{4}-\d{2}-\d{2}-[a-z0-9.-]+\.md$", rf.name):
                    rep.err(_rel(root, rf), "result files are named YYYY-MM-DD-<slug>.md (lower case)")
                check_result_file(root, rep, rf, board, set(setups), feature_ids, today, cache)

    # ---- builds
    for bf in sorted((root / "builds").glob("*/*.yaml")):
        where = _rel(root, bf)
        b = common.load_yaml(bf)
        for e in common.schema_errors(b, build_schema):
            rep.err(where, e)
        if not isinstance(b, dict):
            continue
        board = b.get("board")
        if isinstance(board, str) and bf.parent.name != board.lower():
            rep.err(where, f"directory {bf.parent.name!r} must be {board.lower()!r}")
        m = boards.get(board)
        if m is None:
            rep.err(where, f"board {board!r} has no machines/<board>/machine.yaml")
        elif b.get("setup") not in {s.get("id") for s in m.get("setups", [])}:
            rep.err(where, f"setup {b.get('setup')!r} is not a setup of {board}")
        for r in b.get("results", []) or []:
            if not (root / r).exists():
                rep.err(where, f"result {r} does not exist")
        for sect in ("kernel", "loader", "stage1"):
            for p in ((b.get(sect) or {}).get("patches") or []):
                if p.get("pr") and p["pr"] not in pr_keys:
                    rep.err(where, f"{sect} patch PR {p['pr']} is not in upstream/prs.yaml")
        for name, art in (b.get("outputs") or {}).items():
            if isinstance(art, dict) and art.get("sha256") is None and not art.get("notes"):
                rep.err(where, f"output {name}: sha256 is null; say why in notes (prefix only, per unit, ...)")

    # ---- PR index vs boards, status.json vs index
    for pr in prs_doc.get("prs", []) or []:
        for mb in pr.get("machines", []) or []:
            if mb not in boards:
                rep.warn("upstream/prs.yaml", f"{common.pr_key(pr['repo'], pr['number'])}: board {mb} has no machine file")
    status = common.load_status(root)
    st = status.get("prs", {}) if isinstance(status, dict) else {}
    for k in pr_keys:
        if k not in st:
            rep.warn("upstream/status.json", f"{k} has no entry (run tools/pr_status.py)")
    for k in st:
        if k not in pr_keys:
            rep.err("upstream/status.json", f"{k} is not in upstream/prs.yaml (regenerate it)")
    return rep


def check_cell(root, rep, cw, machine_dir, board, c, setups, draft, feature_ids, pr_keys, today, cache):
    state, kind = c.get("state"), c.get("kind")
    ev = c.get("evidence") or []
    if c.get("setup") not in setups:
        rep.err(cw, f"setup {c.get('setup')!r} is not defined under setups:")
    for u in c.get("upstream") or []:
        if u not in pr_keys:
            rep.err(cw, f"upstream {u} is not listed in upstream/prs.yaml")

    # local links resolve
    local_results = []
    for e in ev:
        path, anchor = resolve_evidence(root, machine_dir, e)
        if path is None:
            continue
        if not path.exists():
            rep.err(cw, f"evidence {e}: file does not exist")
            continue
        text = path.read_text(encoding="utf-8")
        if anchor and anchor not in common.anchors(text):
            rep.err(cw, f"evidence {e}: anchor #{anchor} not found in {path.name}")
        if path.parent == machine_dir / "results":
            r = check_result_file(root, rep, path, board, set(setups), feature_ids, today, cache)
            if r:
                local_results.append(r[0])

    if draft and kind == "native":
        rep.err(cw, "a draft machine holds no native cells (the owner confirms first)")
    if kind == "reported" and state != "reported":
        rep.err(cw, f"kind reported cannot set state {state!r}; use state: reported")
    if state == "reported":
        if kind != "reported":
            rep.err(cw, "state reported needs kind: reported")
        if not ev:
            rep.err(cw, "state reported needs a link to the post or repository the claim comes from")
    if kind == "offline" and state in WORKS:
        rep.err(cw, "offline evidence (built, not run) cannot support a works-* state")

    if state in WORKS:
        if kind != "native":
            rep.err(cw, f"{state} needs kind: native")
        native = [fm for fm in local_results if fm.get("kind") == "native" and fm.get("board") == board]
        if not native:
            rep.err(cw, f"{state} needs at least one evidence link to a result file in machines/{machine_dir.name}/results/ "
                        "with kind: native")
        else:
            newest = max(common.parse_date(fm.get("date")) or common.parse_date("1970-01-01") for fm in native)
            v = common.parse_date(c.get("verified"))
            if v is None:
                rep.err(cw, f"{state} needs verified: {newest.isoformat()} (the date of the newest supporting result)")
            elif v != newest:
                rep.err(cw, f"verified {v.isoformat()} is not the date of the newest supporting result ({newest.isoformat()})")
        if state == "works-daily":
            s = setups.get(c.get("setup")) or {}
            if not s.get("current_build"):
                rep.err(cw, "works-daily needs the setup's current_build recipe (builds/<board>/<name>.yaml)")
    elif state == "attended":
        if not c.get("note"):
            rep.err(cw, "attended needs a note saying what the attended step is")
        if not ev and not c.get("upstream"):
            rep.err(cw, "attended needs a recipe, patch or result link")
    elif state == "prepared":
        if not ev and not c.get("upstream"):
            rep.err(cw, "prepared needs a link to the patches or an upstream PR")
    elif state == "blocked":
        if not ev:
            rep.err(cw, "blocked needs a result file or issue saying what blocks it")
    elif state == "not-realistic":
        if not c.get("note"):
            rep.err(cw, "not-realistic needs one sentence of reason in note")


def write_stale_report(rep, out_dir, today):
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for board, rows in sorted(rep.stale.items()):
        lines = [f"Cells on **{board}** with no supporting result in the last {common.STALE_DAYS} days "
                 f"(as of {today.isoformat()}). Re-run them and add a result, or move them to a state that matches "
                 "what is known now.", "", "| Feature | Setup | State | Last verified |", "|---|---|---|---|"]
        for fid, setup, verified, state in rows:
            lines.append(f"| `{fid}` | {setup} | {state} | {verified or 'never'} |")
        (out / f"{board}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=str(common.ROOT), help="repository root (default: this checkout)")
    ap.add_argument("--today", help="evaluate staleness as of this date (YYYY-MM-DD, default: today in UTC)")
    ap.add_argument("--stale-report", metavar="DIR", help="write DIR/<board>.md for every board with stale cells")
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    ap.add_argument("-q", "--quiet", action="store_true", help="print errors only")
    a = ap.parse_args(argv)
    today = common.parse_date(a.today) if a.today else common.today()
    rep = validate(pathlib.Path(a.root), today)
    for e in rep.errors:
        print(f"ERROR {e}")
    if not a.quiet:
        for w in rep.warnings:
            print(f"WARN  {w}")
    if a.stale_report:
        write_stale_report(rep, a.stale_report, today)
    n_err = len(rep.errors) + (len(rep.warnings) if a.strict else 0)
    if not a.quiet:
        print(f"validate: {len(rep.errors)} error(s), {len(rep.warnings)} warning(s), "
              f"{sum(len(v) for v in rep.stale.values())} stale cell(s)")
    return 1 if n_err else 0


if __name__ == "__main__":
    sys.exit(main())
