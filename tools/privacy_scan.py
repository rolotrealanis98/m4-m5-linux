#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""privacy_scan.py - reject private data, secrets and binaries before they reach the repository.

  python3 tools/privacy_scan.py                         # every tracked and untracked (not ignored) file
  python3 tools/privacy_scan.py machines/j716s README.md
  python3 tools/privacy_scan.py --changed-since origin/main   # files changed against a git ref (CI on a PR)
  python3 tools/privacy_scan.py --list-rules

What it rejects (README, "Privacy"):
  * MAC and Bluetooth addresses (six hex octets, ':' or '-'), except all-zero, broadcast and the RFC 7042
    documentation range 00-00-5E-00-53-xx;
  * IPv4 outside 192.0.2.0/24, 198.51.100.0/24, 203.0.113.0/24 (and loopback/unspecified), IPv6 outside 2001:db8::/32
    (and ::, ::1);
  * serial-number, mlb-serial-number, ECID, nonce, MAC-address and wifi0/bluetooth0 properties with a value;
    Apple serial patterns after "Serial" (10 to 12 upper-case letters and digits);
  * home paths (/Users/<name>, /home/<name>, ~<name>/), user@host shell prompts and ssh/scp targets, LAN host names
    (.local, .lan, .home.arpa, .ts.net, .internal), Wi-Fi passphrases and SSIDs, UUIDs and PARTUUID or UUID assignments;
  * tokens and private keys;
  * hex runs longer than 64 bytes and hexdump lines, unless inside a ```hexdump-reviewed fenced block;
  * ADT dumps (the AAPL-prefixed phandle and unit-string properties, adt/ioreg dump file names);
  * binaries: forbidden extensions (firmware, boot objects, kernels, device trees, images, archives), content by magic
    number (Mach-O, ELF, gzip, zstd, xz, bzip2, cpio, DTB, FAT, APFS, zip, Image4), and any non-text file other than a
    PNG/JPEG under 256 KiB.
A line that is a deliberate false positive may carry 'privacy-scan: allow' plus a reason; reviewers check each one.
Paths listed in .privacy-scan-ignore (glob patterns) are skipped: test fixtures with fake values live there.
"""

from __future__ import annotations

import argparse
import fnmatch
import ipaddress
import os
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MAX_IMAGE = 256 * 1024
ALLOW_MARK = "privacy-scan: allow"
IGNORE_FILE = ".privacy-scan-ignore"

FORBIDDEN_EXT = {
    # boot objects, firmware, kernels, device trees
    ".bin", ".img", ".im4p", ".img4", ".im4m", ".ftab", ".fw", ".raw", ".macho", ".kc", ".kernelcache", ".efi",
    ".dtb", ".dtbo", ".elf", ".ko", ".o", ".so", ".a", ".dylib", ".exe",
    # archives and compressed data
    ".gz", ".tgz", ".xz", ".zst", ".zstd", ".bz2", ".lz4", ".lzma", ".zip", ".7z", ".tar", ".cpio", ".rar",
    # disk and filesystem images, packages
    ".iso", ".dmg", ".ipsw", ".apfs", ".fat", ".vfat", ".qcow2", ".vmdk", ".pkg", ".deb", ".rpm",
    # dumps
    ".adt", ".core", ".dump", ".nvram", ".plist",
}
IMAGE_EXT = {".png", ".jpg", ".jpeg"}
DUMP_NAME_RX = re.compile(r"(?i)(^|[-_.])(adt|ioreg|nvram-dump|device-tree-dump|devicetree-dump)([-_.]|$)")

MAGIC = [
    (0, b"\xfe\xed\xfa\xce", "Mach-O"), (0, b"\xfe\xed\xfa\xcf", "Mach-O"), (0, b"\xce\xfa\xed\xfe", "Mach-O"),
    (0, b"\xcf\xfa\xed\xfe", "Mach-O"), (0, b"\xca\xfe\xba\xbe", "Mach-O universal / Java class"),
    (0, b"\x7fELF", "ELF"), (0, b"\x1f\x8b", "gzip"), (0, b"\x28\xb5\x2f\xfd", "zstd"),
    (0, b"\xfd7zXZ\x00", "xz"), (0, b"BZh", "bzip2"), (0, b"070701", "cpio"), (0, b"070702", "cpio"),
    (0, b"070707", "cpio"), (0, b"\xc7\x71", "cpio (binary)"), (0, b"\xd0\x0d\xfe\xed", "device tree blob"),
    (32, b"NXSB", "APFS container"), (0, b"PK\x03\x04", "zip"), (0, b"7z\xbc\xaf\x27\x1c", "7z"),
    (0, b"MZ", "PE/EFI executable"), (0, b"\x04\x22\x4d\x18", "lz4"),
]


def _doc_ipv4(ip):
    nets = ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24", "127.0.0.0/8")
    return any(ip in ipaddress.ip_network(n) for n in nets) or str(ip) in ("0.0.0.0", "255.255.255.255")


def _ok_ipv4(m):
    try:
        ip = ipaddress.IPv4Address(m.group(0))
    except ValueError:
        return True
    return _doc_ipv4(ip)


def _ok_ipv6(m):
    s = m.group(0)
    if "::" not in s and s.count(":") != 7:
        return True
    try:
        ip = ipaddress.IPv6Address(s)
    except ValueError:
        return True
    if str(ip) in ("::", "::1"):
        return True
    return ip in ipaddress.ip_network("2001:db8::/32")


def _ok_mac(m):
    s = m.group(0).lower().replace("-", ":")
    return s in ("00:00:00:00:00:00", "ff:ff:ff:ff:ff:ff") or s.startswith("00:00:5e:00:53:")


def _ok_serial(m):
    v = m.group(1)
    return not (re.search(r"[A-Z]", v) and re.search(r"[0-9]", v))


_PLACEHOLDER = r"(?!<|\(?(?:removed|redacted|scrubbed|omitted)\b|null\b|none\b|n/a\b|x{4,}|\.\.\.)"
_BEGIN = "-" * 5 + "BEGIN"   # written this way so the scanner does not flag its own source

# (rule id, compiled regex, ok-function or None, message, hint)
RULES = [
    ("mac", re.compile(r"(?<![0-9A-Fa-f:-])[0-9A-Fa-f]{2}([:-])(?:[0-9A-Fa-f]{2}\1){4}[0-9A-Fa-f]{2}(?![0-9A-Fa-f:-])"),
     _ok_mac, "MAC or Bluetooth address", "replace it with <mac>"),
    ("ipv4", re.compile(r"(?<![\w.])(?:(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.){3}(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(?!\w|\.\d)"),
     _ok_ipv4, "IPv4 address outside the documentation ranges", "replace it with <ip> or a 192.0.2.x address"),
    ("ipv6", re.compile(r"(?<![\w:.])(?:[0-9A-Fa-f]{0,4}:){2,7}[0-9A-Fa-f]{0,4}(?![\w:])"),
     _ok_ipv6, "IPv6 address outside 2001:db8::/32", "replace it with <ip> or a 2001:db8:: address"),
    ("identifier-property", re.compile(
        r"(?i)\b(mlb-serial-number|serial-number|serial_number|ioplatformserialnumber|platform-serial|board-serial|ecid|"
        r"apnonce|ap-nonce|boot-nonce|sepnonce|nonce-hash|nonce|mac-address|local-mac-address|wifi0|bluetooth0|"
        r"ethernet0)\b[\"']?\s*[:=]\s*[\"'<\[]?\s*" + _PLACEHOLDER + r"[0-9A-Za-z][^\s,;>'\"\]]{3,}"),
     None, "identifier property with a value (serial, ECID, nonce, MAC)", "delete the line or write <removed>"),
    ("ecid", re.compile(r"(?i)\becid\s+(?:0x)?[0-9a-f]{8,}"), None, "ECID value", "delete it"),
    ("apple-serial", re.compile(r"(?i:serial(?:[\s_-]*(?:number|no\.?|#))?)\s*[:=]?\s*[\"']?([A-Z0-9]{10,12})\b"),
     _ok_serial, "Apple serial number pattern", "delete it"),
    ("home-path", re.compile(r"(?:/Users/(?!<|Shared\b)[A-Za-z0-9._-]+|/home/(?!<)[A-Za-z0-9._-]+|(?<![\w~])~(?!<)[a-z_][a-z0-9_-]*/)"),
     None, "home directory with a user name", "write ~ or /home/<user>"),
    ("prompt", re.compile(r"\b[a-z_][a-z0-9_.-]*@(?!<)[A-Za-z0-9][A-Za-z0-9-]*(?:\.[A-Za-z0-9.-]+)?:[~/][^\s]*\s*[$#](?:\s|$)"
                          r"|\[[a-z_][\w.-]*@(?!<)[\w.-]+\s+[^\]]*\]\s*[$#]"),
     None, "shell prompt with user and host", "write <user>@<host>"),
    ("ssh-target", re.compile(r"\b(?:ssh|scp|sftp|rsync)\s+(?:-\S+\s+)*[a-z_][\w.-]*@(?!<)[A-Za-z0-9][\w.-]*"),
     None, "ssh/scp target with a real user or host", "write <user>@<host>"),
    ("lan-host", re.compile(r"(?i)\b[a-z0-9][\w-]*\.(?:local|lan|home\.arpa|ts\.net|internal|localdomain)\b(?![\w-])"),
     None, "LAN or VPN host name", "write <host>"),
    ("wifi-secret", re.compile(r"(?i)\b(?:psk|passphrase|password|passwd|sae_password)\b\s*[:=]\s*[\"']?" + _PLACEHOLDER + r"\S{4,}"
                               r"|(?i:\bwpa_passphrase\s+)(?!<)\S+\s+(?!<)\S+"
                               r"|(?i:\bssid\s*[:=]\s*)[\"']?" + _PLACEHOLDER + r"[^\s\"']{2,}"),
     None, "Wi-Fi network name or passphrase", "write <ssid> / delete the passphrase"),
    ("uuid", re.compile(r"(?i)\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b|(?i:\b(?:PART)?UUID[=])(?!<)\S+"),
     None, "UUID or PARTUUID", "write <uuid>"),
    ("token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}|\bgithub_pat_[A-Za-z0-9_]{20,}|\bAKIA[0-9A-Z]{16}\b"
                         r"|\bxox[abprs]-[A-Za-z0-9-]{10,}|" + _BEGIN + r" [A-Z ]*PRIVATE KEY-----"),
     None, "token or private key", "remove it and revoke the credential"),
    ("adt-dump", re.compile(r"AAPL,(?:phandle|unit-string)"), None, "ADT dump content", "never commit ADT dumps; quote single properties"),
    ("hex-run", re.compile(r"[0-9A-Fa-f]{129,}"), None, "hex run longer than 64 bytes",
     "trim it, or put a reviewed dump in a ```hexdump-reviewed block"),
    ("hexdump", re.compile(r"^\s*[0-9a-fA-F]{4,16}:?\s+(?:[0-9a-fA-F]{2}\s+){8,}"), None, "hexdump line",
     "trim it, or put a reviewed dump in a ```hexdump-reviewed block"),
]
HEX_RULES = {"hex-run", "hexdump"}


class Finding:
    def __init__(self, path, line, rule, message, hint, excerpt=""):
        self.path, self.line, self.rule, self.message, self.hint, self.excerpt = path, line, rule, message, hint, excerpt

    def __str__(self):
        where = f"{self.path}:{self.line}" if self.line else self.path
        ex = f" ({self.excerpt})" if self.excerpt else ""
        return f"{where}: [{self.rule}] {self.message}{ex}: {self.hint}"


def _mask(s):
    s = s.strip()
    return (s[:3] + "...") if len(s) > 3 else "..."


def scan_text(text, relpath="<text>"):
    findings = []
    fence = None   # None, or the info string of the open fence
    for n, line in enumerate(text.splitlines(), 1):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            fence = None if fence is not None else stripped[3:].strip()
            continue
        if ALLOW_MARK in line:
            continue
        for rid, rx, ok, msg, hint in RULES:
            if rid in HEX_RULES and fence is not None and fence.startswith("hexdump-reviewed"):
                continue
            for m in rx.finditer(line):
                if ok is not None and ok(m):
                    continue
                findings.append(Finding(relpath, n, rid, msg, hint, _mask(m.group(0))))
                break
    return findings


def classify_bytes(data):
    """-> description of a forbidden binary format, or None."""
    for off, magic, name in MAGIC:
        if data[off:off + len(magic)] == magic:
            return name
    if len(data) >= 512 and data[510:512] == b"\x55\xaa" and (b"FAT" in data[0x36:0x3e] or b"FAT32" in data[0x52:0x5a]):
        return "FAT filesystem image"
    if b"IM4P" in data[:64] or b"IMG4" in data[:64] or b"IM4M" in data[:64]:
        return "Image4 firmware"
    return None


def is_text(data):
    if b"\x00" in data[:8192]:
        return False
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True


def scan_file(path, relpath=None):
    relpath = relpath or str(path)
    p = pathlib.Path(path)
    findings = []
    ext = p.suffix.lower()
    name = p.name
    if ext in FORBIDDEN_EXT:
        findings.append(Finding(relpath, 0, "binary-ext", f"forbidden file type '{ext}'",
                                "no firmware, boot objects, kernels, device trees, archives or dumps: record a sha256 instead"))
    if DUMP_NAME_RX.search(p.stem):
        findings.append(Finding(relpath, 0, "dump-name", "file name looks like an ADT/ioreg/NVRAM dump",
                                "never commit dumps; quote single properties in a topic or result"))
    data = p.read_bytes()
    kind = classify_bytes(data)
    if kind and not (ext in IMAGE_EXT):
        findings.append(Finding(relpath, 0, "binary-magic", f"{kind} content", "remove the binary; record its sha256 in builds/"))
    if not is_text(data):
        if ext in IMAGE_EXT:
            if len(data) > MAX_IMAGE:
                findings.append(Finding(relpath, 0, "binary-size", f"image larger than {MAX_IMAGE // 1024} KiB",
                                        "shrink or crop the screenshot"))
        elif not kind and ext not in FORBIDDEN_EXT:
            findings.append(Finding(relpath, 0, "binary", "non-text file", "only text, and PNG/JPEG under 256 KiB, are allowed"))
        return findings
    findings += scan_text(data.decode("utf-8"), relpath)
    return findings


def load_ignores(root):
    f = root / IGNORE_FILE
    if not f.exists():
        return []
    pats = []
    for line in f.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            pats.append(line)
    return pats


def ignored(rel, pats):
    for pat in pats:
        if pat.endswith("/**") and (rel == pat[:-3] or rel.startswith(pat[:-2])):
            return True
        if pat.endswith("/") and rel.startswith(pat):
            return True
        if fnmatch.fnmatch(rel, pat):
            return True
    return False


def list_files(root, paths=None, changed_since=None):
    root = pathlib.Path(root)
    out = []
    if changed_since:
        r = subprocess.run(["git", "-C", str(root), "diff", "--name-only", "--diff-filter=ACMR", changed_since, "--"],
                           capture_output=True, text=True, check=True)
        out = [root / x for x in r.stdout.splitlines() if x]
    elif paths:
        for p in paths:
            p = pathlib.Path(p)
            p = p if p.is_absolute() else (pathlib.Path.cwd() / p)
            if p.is_dir():
                out += [q for q in sorted(p.rglob("*")) if q.is_file() and ".git" not in q.relative_to(p).parts]
            elif p.exists():
                out.append(p)
    else:
        r = subprocess.run(["git", "-C", str(root), "ls-files", "-co", "--exclude-standard"],
                           capture_output=True, text=True)
        if r.returncode == 0:
            out = [root / x for x in r.stdout.splitlines() if x]
        else:
            for dp, dns, fns in os.walk(root):
                dns[:] = [d for d in dns if d != ".git"]
                out += [pathlib.Path(dp) / f for f in fns]
    return [p for p in out if p.is_file()]


def scan(root=ROOT, paths=None, changed_since=None):
    root = pathlib.Path(root).resolve()
    pats = load_ignores(root)
    findings = []
    for p in list_files(root, paths, changed_since):
        try:
            rel = p.resolve().relative_to(root).as_posix()
        except ValueError:
            rel = str(p)
        if ignored(rel, pats):
            continue
        findings += scan_file(p, rel)
    return findings


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("paths", nargs="*", help="files or directories (default: the whole repository)")
    ap.add_argument("--root", default=str(ROOT), help="repository root (for .privacy-scan-ignore and git)")
    ap.add_argument("--changed-since", metavar="REF", help="scan only files changed against this git ref")
    ap.add_argument("--list-rules", action="store_true")
    a = ap.parse_args(argv)
    if a.list_rules:
        for rid, _, _, msg, hint in RULES:
            print(f"{rid:20} {msg}: {hint}")
        print(f"{'binary-*':20} forbidden extensions, magic numbers, non-text files; images up to {MAX_IMAGE // 1024} KiB")
        return 0
    findings = scan(a.root, a.paths, a.changed_since)
    for f in findings:
        print(f)
    print(f"privacy_scan: {len(findings)} finding(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
