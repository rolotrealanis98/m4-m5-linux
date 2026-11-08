# Contributing to M4-M5 Linux

Thanks for helping. This repository tracks what runs on M4 and M5 Macs; it does not hold code. Read the
[README](README.md) first for the states, the evidence rules, the AI policy and the governance.

By opening a pull request you offer your text under the licence of the path you touch: CC-BY-SA-4.0 for documentation
and data, MIT for `tools/`, `tests/` and `.github/workflows/`.

## What a good pull request looks like

- It touches one board, one topic, or the tooling, not all three.
- Every changed state has an evidence link, and every `works-*` state links a result file from that board.
- The log excerpts are scrubbed (see below) and `tools/privacy_scan.py` passes.
- `tools/validate.py` passes and `tools/gen.py --check` passes (run `python3 tools/gen.py` and commit the result).
- No binaries, no firmware, no ADT dumps, no download links to unofficial binaries.

## Adding a machine

See "How to add a machine" in the README. Board directories are lower case (`machines/j714s/`); the `board:` field
keeps the usual spelling (`J714s`). Model name, `MacNN,N` identifier and SoC are fields, so a search by any of them
finds the machine on the site.

If you write an entry for a machine that is not yours (from its owner's public posts), set `draft: true`, name the
`owner:`, mark every cell `state: reported` with `kind: reported`, and link the exact post or README section each claim
comes from. Do not copy text or files from repositories that have no licence: link them. The owner converts the entry to
`native` when they agree.

## Writing a result file

```markdown
---
date: 2026-11-07T23:16Z          # UTC, start of the run
board: J716s
setup: j716s-aurora73             # a setup id from machine.yaml
kind: native                     # native results only; claims go in machine.yaml as kind: reported
build: builds/j716s/daily-n1k.yaml
kernel: 7.3.0-g36845aa5f650      # uname -r
payload_sha256_prefix: 512a1c00  # or payload_sha256 with the full hash
firmware: { os: "27.3 beta 1 (26C5035r)", system: "27.3 beta 1 (26C5035r)" }
attended: false                  # true when a person was at the machine; say what they did in the body
source: https://github.com/<you>/<status-repo>/blob/<commit>/<path>#<section>
features: [cpu.smp, wifi-bt.wifi]
---

## What was booted
## Results
| Feature / action | pass, fail, not tested | Detail |
## Log excerpts (scrubbed)
## Not tested
```

- One run per file (or one summary of a short run series, with each run as its own section). Never edit a merged result
  except to append a `## Correction` section that says what was wrong.
- Give pass, fail or not tested for each action, report both firmware fields, and list what was not tested.
- Quote log lines literally and trimmed. Never paste whole journals.
- Link your status repository by commit permalink so the link survives rewrites there.

## Scrubbing logs

Remove or replace before you commit:

| Remove | Replace with |
|---|---|
| Serial numbers, ECID, nonces, `/chosen` boot-security values | delete the line, or `<removed>` |
| MAC and Bluetooth addresses | `<mac>` |
| IPv4/IPv6 addresses (LAN, VPN, public) | `<ip>`, or a documentation address (192.0.2.x, 2001:db8::x) |
| Host names, user names, home paths, shell prompts | `<host>`, `<user>`, `~` |
| Wi-Fi network names and passphrases, PARTUUIDs and filesystem UUIDs | `<ssid>`, `<uuid>` |
| Per-unit values (calibration, tunables, voltage tables seen on one unit only) | the property name and "per unit, read at boot" |
| Firmware images, boot objects, ADT/device-tree dumps, NVRAM dumps | nothing: never commit them, not even redacted |

`tools/privacy_scan.py` catches the patterns it can (MAC addresses, IP addresses outside the documentation ranges,
serial and ECID properties, Apple serial patterns, home paths, prompts, UUIDs, tokens, binaries and firmware by magic
number and extension). A line that is a deliberate false positive can carry the marker `privacy-scan: allow` with a
reason in the same line; reviewers check every use.

## Build recipes

`builds/<board>/<name>.yaml` records the upstream repositories and commits, the patch lists, the kernel config, the
boot arguments (with no private values) and the sha256 of every ingredient and output. Use the full hash; a prefix may
appear in prose next to it. When the source notebook only recorded a prefix, write `sha256: null` with
`sha256_prefix:` and say so in `notes`. Ingredients that are personalised per unit (the N1 firmware, anything built
from the unit's own firmware) are described, never hashed or linked.

## Upstream PRs

Add a PR to `upstream/prs.yaml` (repo, number, title, machines, features) when it opens. `upstream/status.json` is
written by `tools/pr_status.py` through the bot's pull request; do not edit it by hand.

## Patch mirrors

Not wanted by default: code goes upstream. A board may keep a read-only mirror under `machines/<board>/patches/` only for
patches that have no upstream PR yet and a clear target, each series with a `PROVENANCE.yaml` (source repository,
commit, author, licence, upstream PR or target). Kernel patches keep their GPL-2.0 SPDX lines and the human author's
`Signed-off-by`.

## "Can we have an integration branch?"

No: this repository has no code. Omarchy's T6050 base is `omacom/linux-aurora` #404 (kernel) and `omacom/m1n1` #30
(loader); boards stack on them (the J716s as #413 and #33-#37). Aurora Silicon's `integration/aurora` carries the
driver work. Send patches there and add the PRs to `upstream/prs.yaml`.

## Running the checks

```sh
python3 -m pip install pyyaml pytest
python3 tools/validate.py && python3 tools/privacy_scan.py && python3 tools/gen.py --check && python3 -m pytest -q tests
```
