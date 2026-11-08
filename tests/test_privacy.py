# SPDX-License-Identifier: MIT
import gzip
import struct

import pytest

import privacy_scan as ps
from conftest import FIX, ROOT

# Fake values are assembled at run time so this file itself passes the scanner.
FAKE_MAC = ":".join(["02", "5e", "aa", "10", "20", "30"])
FAKE_LAN = ".".join(["192", "168", "1", "1"])
FAKE_PRIV = ".".join(["10", "0", "0", "9"])

LEAKS = [l.split("\t", 1) for l in (FIX / "privacy" / "leaks.tsv").read_text().splitlines()
         if l and not l.startswith("#")]


@pytest.mark.parametrize("rule,line", LEAKS, ids=[f"{r}-{i}" for i, (r, _) in enumerate(LEAKS)])
def test_leak_is_caught(rule, line):
    rules = {f.rule for f in ps.scan_text(line)}
    assert rule in rules, f"{line!r} not caught by {rule} (got {rules})"


def test_clean_lines_pass():
    findings = ps.scan_text((FIX / "privacy" / "clean.txt").read_text())
    assert findings == [], "\n".join(map(str, findings))


def test_allow_marker_skips_line():
    assert ps.scan_text("ip 10.1.2.3 in an RFC example  privacy-scan: allow (quoted from RFC 1918)") == []


def test_hexdump_outside_reviewed_fence_is_caught():
    text = "```\n00000000: 7f 45 4c 46 02 01 01 00 00 00 00 00 00 00 00 00  .ELF\n```\n"
    assert {f.rule for f in ps.scan_text(text)} == {"hexdump"}


def test_output_masks_the_value():
    f = ps.scan_text(f"address {FAKE_MAC}")[0]
    assert FAKE_MAC not in str(f)


def _write(tmp_path, name, data):
    p = tmp_path / name
    p.write_bytes(data)
    return p


@pytest.mark.parametrize("name,data,rule", [
    ("kernel.txt", b"\x7fELF\x02\x01\x01" + b"\x00" * 64, "binary-magic"),
    ("m1n1.txt", struct.pack("<I", 0xfeedfacf) + b"\x00" * 64, "binary-magic"),
    ("initrd.txt", gzip.compress(b"hello"), "binary-magic"),
    ("board.txt", b"\xd0\x0d\xfe\xed" + b"\x00" * 60, "binary-magic"),
    ("payload.bin", b"just text", "binary-ext"),
    ("t6050-j716s.dtb", b"text", "binary-ext"),
    ("firmware.im4p", b"text", "binary-ext"),
    ("blob.dat", bytes(range(256)) * 4, "binary"),
    ("j716s-adt.txt", b"nothing private here", "dump-name"),
])
def test_binaries_and_dumps_are_rejected(tmp_path, name, data, rule):
    p = _write(tmp_path, name, data)
    assert rule in {f.rule for f in ps.scan_file(p, name)}


def test_small_png_allowed_large_png_rejected(tmp_path):
    png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
    assert ps.scan_file(_write(tmp_path, "shot.png", png), "shot.png") == []
    big = b"\x89PNG\r\n\x1a\n" + b"\x00" * (ps.MAX_IMAGE + 1)
    assert {f.rule for f in ps.scan_file(_write(tmp_path, "big.png", big), "big.png")} == {"binary-size"}


def test_scan_respects_ignore_file(tmp_path):
    (tmp_path / ".privacy-scan-ignore").write_text("fixtures/**\n")
    (tmp_path / "fixtures").mkdir()
    (tmp_path / "fixtures" / "fake.txt").write_text(f"gateway {FAKE_LAN}\n")
    (tmp_path / "real.txt").write_text(f"gateway {FAKE_LAN}\n")
    found = ps.scan(tmp_path, [str(tmp_path)])
    assert [f.path for f in found] == ["real.txt"]


def test_cli_exit_codes(tmp_path):
    (tmp_path / "ok.txt").write_text("nothing to see\n")
    assert ps.main(["--root", str(tmp_path), str(tmp_path / "ok.txt")]) == 0
    (tmp_path / "bad.txt").write_text(f"inet {FAKE_PRIV}\n")
    assert ps.main(["--root", str(tmp_path), str(tmp_path / "bad.txt")]) == 1


def test_rules_listed():
    assert ps.main(["--list-rules"]) == 0
