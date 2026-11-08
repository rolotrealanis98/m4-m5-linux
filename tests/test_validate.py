# SPDX-License-Identifier: MIT
import datetime as dt
import shutil

import common
import validate
from conftest import FIX

ON = dt.date(2026, 11, 7)


def run(root, on=ON):
    return validate.validate(root, on)


def test_valid_mini_repo_passes(mini_repo):
    rep = run(mini_repo)
    assert rep.errors == [], "\n".join(rep.errors)
    assert rep.stale == {}


def test_invalid_machine_file(mini_repo):
    shutil.copy(FIX / "machine-invalid.yaml", mini_repo / "machines" / "j999t" / "machine.yaml")
    # the build points at test-setup, which still exists; results of second-setup now name an unknown setup
    errs = "\n".join(run(mini_repo).errors)
    for expected in [
        "unknown key 'color'",
        "kind reported cannot set state 'works-daily'",
        "works-daily needs kind: native",
        "works-daily needs the setup's current_build",
        "results/2026-11-09-missing.md: file does not exist",
        "anchor #no-such-heading not found",
        "verified 2026-10-01 is not the date of the newest supporting result (2026-11-01)",
        "unknown feature id 'gpu.warp-drive'",
        "attended needs a note",
        "setup 'nobody' is not defined",
        "not-realistic needs one sentence of reason",
        "upstream example/linux#999 is not listed in upstream/prs.yaml",
        "'shiny' is not one of",
    ]:
        assert expected in errs, f"missing error: {expected}\n{errs}"


def _edit_machine(root, fn):
    p = root / "machines" / "j999t" / "machine.yaml"
    m = common.load_yaml(p)
    fn(m)
    import yaml
    p.write_text(yaml.safe_dump(m, sort_keys=False))


def test_works_needs_a_result_file_not_a_url(mini_repo):
    def f(m):
        m["features"]["storage.nvme"][0]["evidence"] = ["https://example.com/log"]
    _edit_machine(mini_repo, f)
    assert any("needs at least one evidence link to a result file" in e for e in run(mini_repo).errors)


def test_result_board_must_match(mini_repo):
    r = mini_repo / "machines" / "j999t" / "results" / "2026-11-01-boot.md"
    r.write_text(r.read_text().replace("board: J999t", "board: J716s", 1))
    errs = "\n".join(run(mini_repo).errors)
    assert "front matter board 'J716s' is not 'J999t'" in errs


def test_result_file_name_date_must_match(mini_repo):
    d = mini_repo / "machines" / "j999t" / "results"
    (d / "2026-11-03-other.md").write_text((d / "2026-11-02-second.md").read_text())
    assert any("differs from front matter date" in e for e in run(mini_repo).errors)


def test_draft_holds_no_native_cells(mini_repo):
    _edit_machine(mini_repo, lambda m: m.update(draft=True))
    assert any("a draft machine holds no native cells" in e for e in run(mini_repo).errors)


def test_reported_state_needs_reported_kind_and_link(mini_repo):
    def f(m):
        m["features"]["wifi-bt.wifi"][0].update(kind="native", evidence=[])
    _edit_machine(mini_repo, f)
    errs = "\n".join(run(mini_repo).errors)
    assert "state reported needs kind: reported" in errs
    assert "state reported needs a link" in errs


def test_stale_cells_flagged_and_reported(mini_repo, tmp_path):
    later = dt.date(2026, 12, 15)
    rep = run(mini_repo, later)
    assert rep.errors == []
    assert {fid for fid, *_ in rep.stale["J999t"]} == {"cpu.smp", "storage.nvme"}
    validate.write_stale_report(rep, tmp_path / "stale", later)
    text = (tmp_path / "stale" / "J999t.md").read_text()
    assert "`cpu.smp`" in text and "2026-11-01" in text


def test_future_result_rejected(mini_repo):
    rep = run(mini_repo, dt.date(2026, 10, 20))
    assert any("is in the future" in e for e in rep.errors)


def test_status_json_must_match_index(mini_repo):
    p = mini_repo / "upstream" / "status.json"
    p.write_text(p.read_text().replace("example/linux#1", "example/linux#2"))
    rep = run(mini_repo)
    assert any("example/linux#2 is not in upstream/prs.yaml" in e for e in rep.errors)


def test_cli(mini_repo):
    assert validate.main(["--root", str(mini_repo), "--today", "2026-11-07", "-q"]) == 0
    assert validate.main(["--root", str(mini_repo), "--today", "2026-12-31", "--strict", "-q"]) == 1


def test_schema_checker_subset():
    s = {"type": "object", "required": ["a"], "additionalProperties": False,
         "properties": {"a": {"type": "string", "pattern": "^x"}, "b": {"anyOf": [{"type": "null"}, {"type": "integer"}]}}}
    assert common.schema_errors({"a": "xy", "b": None}, s) == []
    errs = common.schema_errors({"a": "y", "b": "no", "c": 1}, s)
    assert len(errs) == 3


def test_anchor_slugs():
    text = "# Result (R3-S, 2026-11-07 09:17 UTC)\n## Wi-Fi\n## Wi-Fi\n```\n# not a heading\n```\n"
    assert common.anchors(text) == {"result-r3-s-2026-11-07-0917-utc", "wi-fi", "wi-fi-1"}
