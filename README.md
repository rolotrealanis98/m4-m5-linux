# M4-M5 Linux

A shared tracker for Linux on Macs with the M4 and M5 chip families: which machine runs what, how sure we are, with
which build, and where the code lives upstream. It holds status, dated result logs, tested build recipes and topic
notes. **It holds no code and no binaries.**

> **Where this repository lives.** The name M4-M5 Linux and its home were agreed on
> [omacom/linux-aurora #293](https://github.com/omacom/linux-aurora/issues/293#issuecomment-6716546581): a new
> repository under `omacom`, once the omacom maintainers confirm. Until then it is staged as
> `rolotrealanis98/m4-m5-linux` and will be **transferred to `omacom/m4-m5-linux`** in one step (a GitHub transfer
> keeps history, issues and pull requests, and redirects the old URLs). If that confirmation does not come, the
> fallback is a new neutral organisation with the same owners. Until a transfer, this project is independent of Apple,
> Asahi Linux, omacom/Omarchy and Aurora Silicon, and speaks for none of them.

## Status

The matrix is generated from `machines/<board>/machine.yaml` by `tools/gen.py`. Each cell is the state of the newest
entry for that feature; `*` marks a stale cell (no supporting result in the 30 days before the last upstream refresh)
and `R` a cell reproduced on two setups. Draft machines (entries written from their owners' public posts and not yet confirmed by them) show
`reported` cells. The [site](site/index.html) has the same data with evidence links on every cell.

<!-- BEGIN GENERATED: matrix -->
#### M5 family

| Feature | [J714c](machines/j714c/machine.yaml) (draft) | [J714s](machines/j714s/machine.yaml) (draft) | [J716s](machines/j716s/machine.yaml) |
|---|---|---|---|
| Untethered boot (`boot.untethered`) | reported | reported | works (daily) |
| Boot safety and recovery (`boot.safety`) | untested | reported | works (daily) |
| Omarchy boot chain (m1n1, U-Boot, Limine, EFI kernel) (`boot.omarchy-chain`) | reported | untested | attended |
| All CPU cores (`cpu.smp`) | reported | reported | works (daily) |
| CPU frequency scaling (`cpu.cpufreq`) | reported | reported | works (daily) |
| CPU idle (WFI) (`cpu.idle`) | untested | reported | works (daily) |
| Internal NVMe (`storage.nvme`) | reported | reported | works (daily) |
| Built-in keyboard (`input.keyboard`) | reported | reported | works (daily) |
| Keyboard backlight (`input.kbd-backlight`) | reported | reported | works (daily) |
| Built-in trackpad (`input.trackpad`) | reported | reported | works (daily) |
| Trackpad palm and thumb handling (`input.trackpad-palm`) | untested | untested | attended |
| Battery and charger (`smc.battery`) | reported | reported | works (daily) |
| Fans and sensors (`smc.sensors`) | reported | reported | works (daily) |
| Lid and power button events (`smc.lid`) | reported | reported | works (daily) |
| Suspend to idle (`sleep.s2idle`) | reported | reported | works (daily) |
| USB host on the Type-C ports (`usb.host`) | reported | untested | works (daily) |
| Netfilter and WireGuard in the kernel (`net.netfilter`) | reported | reported | works (daily) |
| Wi-Fi (`wifi-bt.wifi`) | reported | reported | works (daily) |
| Wi-Fi 6 GHz (`wifi-bt.wifi-6ghz`) | reported | untested | untested |
| Bluetooth controller (`wifi-bt.bt`) | reported | untested | works (daily) |
| Bluetooth pairing (`wifi-bt.bt-pairing`) | untested | untested | attended |
| Speakers (`audio.speakers`) | reported | untested | works (daily) |
| Microphone (`audio.mic`) | reported | untested | works (daily) |
| Headphone jack (`audio.jack`) | untested | untested | attended |
| Tuned speaker profile (`audio.speaker-profile`) | untested | untested | attended |
| GPU firmware and DRM device (`gpu.firmware`) | reported | reported | works (daily) |
| Vulkan on the GPU (`gpu.vulkan`) | untested | untested | works (daily) |
| OpenGL on the GPU (any path) (`gpu.gl`) | untested | untested | works (daily) |
| Native Gallium OpenGL (`gpu.gl-native`) | untested | untested | works (daily) |
| Desktop session (`desktop.session`) | reported | reported | works (daily) |
| Internal panel through the DCP (`display.dcp`) | reported | reported | works (test) |
| High refresh rate and VRR (`display.refresh`) | untested | untested | works (test) |
| Panel brightness (`display.brightness`) | reported | reported | blocked |
| External displays (`display.external`) | untested | untested | prepared |
| NVRAM read (`nvram.read`) | untested | untested | works (daily) |
| NVRAM write (`nvram.write`) | untested | untested | untested |
| PMP coprocessor (`power.pmp`) | reported | untested | untested |
| Power-management controller (observe) (`power.pmc-observe`) | untested | untested | works (test) |
| Power-management controller (control) (`power.pmc-control`) | untested | untested | attended |
| Thermal zones (`power.thermal`) | untested | untested | prepared |
| Camera ISP power domains and DARTs (`camera.isp-power`) | untested | untested | works (test) |
| Camera capture (`camera.capture`) | untested | untested | attended |
| Thunderbolt / USB4 (`thunderbolt`) | untested | untested | blocked |
| Hardware video decode (`video.decode`) | untested | untested | prepared |
| Hardware video encode (`video.encode`) | untested | untested | not realistic |
| ProRes engine (`video.prores`) | untested | untested | not realistic |
| Neural Engine (`ane`) | untested | untested | prepared |
| Touch ID (`touchid`) | untested | untested | not realistic |

States and evidence rules: see [States and evidence](#states-and-evidence). `R` = reproduced on two setups, `*` = stale.
<!-- END GENERATED: matrix -->

### Machines

<!-- BEGIN GENERATED: machines -->
| Board | Model | Identifier | SoC | Owners | Entry | Setups | Current build |
|---|---|---|---|---|---|---|---|
| [J714c](machines/j714c/machine.yaml) | MacBook Pro (14-inch, M5 Max) | Mac17,7 | T6050 | [@edimoldovan](https://github.com/edimoldovan) | draft (from public posts, not yet confirmed) | edimoldovan-omarchy | none |
| [J714s](machines/j714s/machine.yaml) | MacBook Pro (14-inch, M5 Pro) | Mac17,9 | T6050 | [@TripleU613](https://github.com/TripleU613), [@betizzel](https://github.com/betizzel) | draft (from public posts, not yet confirmed) | triple-m5boot, betizzel-m1n1 | none |
| [J716s](machines/j716s/machine.yaml) | MacBook Pro (16-inch, M5 Pro) | Mac17,8 | T6050 | [@rolotrealanis98](https://github.com/rolotrealanis98) | confirmed | j716s-aurora73, j716s-legacy72 | [daily-n1k](builds/j716s/daily-n1k.yaml) |
<!-- END GENERATED: machines -->

### Upstream pull requests

Hand-written index in [`upstream/prs.yaml`](upstream/prs.yaml); live state in
[`upstream/status.json`](upstream/status.json), refreshed daily by `tools/pr_status.py`.

<!-- BEGIN GENERATED: upstream -->
| PR | Title | Machines | Features | State |
|---|---|---|---|---|
| [aurora-silicon/linux#937](https://github.com/aurora-silicon/linux/pull/937) | PCI: apple: adopt the T6050 root ports the boot loader trained | J716s, J716c | `wifi-bt.wifi` | open |
| [aurora-silicon/linux#945](https://github.com/aurora-silicon/linux/pull/945) | arm64: dts: apple: add the J716c (MacBook Pro 16-inch, M5 Max) | J716c, J716s | `boot.untethered` | open |
| [aurora-silicon/linux#946](https://github.com/aurora-silicon/linux/pull/946) | J716c: Thunderbolt 5 and USB4 on the right USB-C port | J716c, J716s | `thunderbolt` | open |
| [aurora-silicon/linux#1012](https://github.com/aurora-silicon/linux/pull/1012) | drm/asahi, drm/apple: M5 GPU and firmware-27 display on integration/aurora | J716s | `gpu.firmware`, `display.dcp` | open |
| [aurora-silicon/linux#1082](https://github.com/aurora-silicon/linux/pull/1082) | soc: apple: rtkit: wait up to 10 s for a handshake reply | J716s, J714s | `storage.nvme` | open |
| [aurora-silicon/linux#1083](https://github.com/aurora-silicon/linux/pull/1083) | HID: dockchannel-hid: settle 50 ms after releasing the AFE reset | J716s | `input.trackpad` | open |
| [aurora-silicon/linux#1084](https://github.com/aurora-silicon/linux/pull/1084) | hwmon: (macsmc) keep a fan whose optional keys are missing | J716s | `smc.sensors` | open |
| [aurora-silicon/linux#1152](https://github.com/aurora-silicon/linux/pull/1152) | arm64: idle: T6050 idles in WFI even with idle=nop | J716s | `cpu.idle` | open |
| [aurora-silicon/linux#1160](https://github.com/aurora-silicon/linux/pull/1160) | Input: macsmc-input - confirm a lid-open report during system sleep | J716s | `sleep.s2idle`, `smc.lid` | open |
| [aurora-silicon/linux#1167](https://github.com/aurora-silicon/linux/pull/1167) | arm64: dts: apple: add the J716s (MacBook Pro 16-inch, M5 Pro) | J716s | `boot.untethered`, `storage.nvme`, `input.keyboard`, `input.trackpad`, `smc.battery`, `smc.sensors`, `usb.host` | open |
| [aurora-silicon/linux#1173](https://github.com/aurora-silicon/linux/pull/1173) | drm/asahi: M5: InitData for the macOS 27.2 and 27.3 firmware (G17S bring-up on J716s) | J716s | `gpu.firmware`, `gpu.vulkan`, `gpu.gl` | open |
| [aurora-silicon/linux#1174](https://github.com/aurora-silicon/linux/pull/1174) | drm/apple: firmware 27.3 IOMFB method table and swap layout | J716s | `display.dcp` | open |
| [aurora-silicon/linux#1182](https://github.com/aurora-silicon/linux/pull/1182) | PCI: apple: train a T6050 root port the boot loader left down (J716s N1) | J716s, J714c | `wifi-bt.wifi`, `wifi-bt.bt` | open |
| [aurora-silicon/linux#1183](https://github.com/aurora-silicon/linux/pull/1183) | arm64: dts: apple: t6050-j716s: let the kernel train the N1 root port (on #1167) | J716s | `wifi-bt.wifi`, `wifi-bt.bt` | open |
| [aurora-silicon/m1n1#65](https://github.com/aurora-silicon/m1n1/pull/65) | kboot: train the T6050 N1 link and fill its hand-off (J716s Wi-Fi/Bluetooth) | J716s | `wifi-bt.wifi`, `wifi-bt.bt` | open |
| [aurora-silicon/mesa#194](https://github.com/aurora-silicon/mesa/pull/194) | asahi: native Gallium GL on the M5 Pro and M5 Max (G17S, G17C) | J716s, J714c | `gpu.gl-native` | open |
| [omacom/linux-aurora#404](https://github.com/omacom/linux-aurora/pull/404) | Add the T6050 (M5 Max) and the 14-inch MacBook Pro (J714c) | J714c | `cpu.smp`, `cpu.cpufreq`, `input.keyboard`, `input.trackpad`, `smc.battery`, `smc.sensors`, `wifi-bt.wifi` | open |
| [omacom/linux-aurora#413](https://github.com/omacom/linux-aurora/pull/413) | Add the 16-inch MacBook Pro with the M5 Pro (J716s) | J716s | `boot.untethered` | open |
| [omacom/m1n1#30](https://github.com/omacom/m1n1/pull/30) | T6050 (M5 Max, J714c): boot from disk through the Omarchy chain | J714c | `boot.untethered`, `boot.omarchy-chain` | open |
| [omacom/m1n1#33](https://github.com/omacom/m1n1/pull/33) | smp: T6050: forward secondaries whose RVBAR is locked to the stage 1 base (stacked on #30) | J716s | `cpu.smp`, `boot.untethered` | open |
| [omacom/m1n1#34](https://github.com/omacom/m1n1/pull/34) | pcie, kboot: T6050: optional N1 (Wi-Fi/Bluetooth) training and hand-off behind chosen.asahi,t6050-n1 (stacked on #33) | J716s | `wifi-bt.wifi`, `wifi-bt.bt` | open |
| [omacom/m1n1#35](https://github.com/omacom/m1n1/pull/35) | kboot: T6050: internal display hand-off for the firmware-27 DCP driver, opt-in (stacked on #37) | J716s | `display.dcp` | open |
| [omacom/m1n1#36](https://github.com/omacom/m1n1/pull/36) | wdt: leave the watchdog armed when the boot-args say m1n1.wdt=keep | J716s | `boot.safety` | open |
| [omacom/m1n1#37](https://github.com/omacom/m1n1/pull/37) | kboot_gpu: T6050: hand the GPU to the G17 driver from the ADT (stacked on #34) | J716s | `gpu.firmware` | open |
| [omacom/omarchy-mac-pkgs#103](https://github.com/omacom/omarchy-mac-pkgs/pull/103) | Cover the 16-inch M5 Pro (J716s) in the audio tests and the manual | J716s | `audio.speakers`, `audio.mic` | open |

State from `upstream/status.json`, fetched 2026-11-08T03:32:54Z.
<!-- END GENERATED: upstream -->

## What lives here

| Path | What |
|---|---|
| `machines/<board>/machine.yaml` | The status source for one board (`j716s`, `j714c`, `j714s`, ...): setups, and one cell list per feature |
| `machines/<board>/results/YYYY-MM-DD-<slug>.md` | Result logs: one run (or one summary of a run series) per file, scrubbed log lines, never edited after merge except for a `Correction` section |
| `builds/<board>/<name>.yaml` | Tested build recipes: upstream repos and commits, patch lists, config, boot arguments and the sha256 of every ingredient and output. Never the binary |
| `topics/<area>/` | What is known for a SoC across machines, written once, with links to the machine results and the upstream PRs |
| `upstream/prs.yaml`, `upstream/status.json` | The upstream PR index and its generated live state |
| `schema/` | `features.yaml` (feature ids and what "works" means for each) and the JSON Schemas for machines, builds, PR index and result front matter |
| `tools/` | `validate.py`, `gen.py`, `privacy_scan.py`, `pr_status.py` (Python 3, standard library + PyYAML) |
| `site/` | The generated static site, published with GitHub Pages |

## Code stays upstream

This is a tracker, not a fork. There are no kernel, m1n1, U-Boot or Mesa branches here and no integration branch.

- Kernel work goes as PRs to `omacom/linux-aurora` and `aurora-silicon/linux`.
- Loader work goes to `omacom/m1n1` and `aurora-silicon/m1n1`.
- Packages go to `omacom/omarchy-mac-pkgs`; Mesa work to `aurora-silicon/mesa`.
- The tracker indexes those PRs in `upstream/prs.yaml` and shows their state. A cell's `upstream:` field names the PRs
  that carry its code.
- Personal status repositories (the owners' lab notebooks) stay the detailed record; the tracker carries the summary and
  links to them by commit permalink.

If you are looking for "the integration branch": Omarchy's T6050 base is `omacom/linux-aurora` #404 (kernel) and
`omacom/m1n1` #30 (loader), and Aurora Silicon's `integration/aurora` carries the driver work they pull from.

## States and evidence

Every cell has a **state** and a **kind** of evidence. The validator (`tools/validate.py`) enforces the rules below on
every pull request.

| State | Meaning | Evidence required |
|---|---|---|
| `works-daily` | Part of the payload the owner boots day to day | A result file from this board with `kind: native`, plus the setup's build recipe |
| `works-test` | Passed on a test payload or test tree, not in the daily yet | A result file from this board with `kind: native` |
| `attended` | Built; the next step needs a person at the machine (cold start, listening test, plug test) | A recipe, patch or result link, and a note saying what the attended step is |
| `prepared` | Patches or device tree written, not booted | A link to the patches or PR |
| `blocked` | Tried and failed, or needs something not available (firmware, documentation, hardware) | A result file or issue saying what blocks it |
| `not-realistic` | Not planned (for example Touch ID behind the Secure Enclave) | One sentence of reason |
| `untested` | Default. Nothing known | None |
| `reported` | Someone's public claim, linked, not yet confirmed by a result file here | A link to the post or repository it comes from; only with `kind: reported` |

| Kind | Meaning |
|---|---|
| `native` | Run on this board by this setup; the result file says what was run and quotes the log lines |
| `reported` | Someone else's claim, not reproduced here. It never sets a `works-*` state |
| `offline` | Built and reviewed, not run |

Rules:

1. A `works-*` state needs `kind: native` and at least one evidence link to a result file in `machines/<board>/results/`
   that exists, whose anchor exists, and whose front matter has a `date`, the same `board` and `kind: native`.
2. A result file carries a log excerpt for each pass line, or a clear statement of what a person saw or heard (a tone
   heard, the lid woke the machine). "It works" without either is not evidence. A driver probe is not a pass.
3. A claim that a fix applies to another board is entered on that board as `kind: reported`, with a link. It becomes
   `native` only with a result from that board.
4. `reproduced` is computed, never written: two setups with `native` evidence for the same feature.
5. A cell whose newest supporting result is older than 30 days is flagged **stale**; a weekly job opens one issue per
   board listing them.
6. Every `upstream:` reference must be listed in `upstream/prs.yaml`.
7. What "works" means for each feature is one sentence in [`schema/features.yaml`](schema/features.yaml). A software
   renderer, a loaded driver or a successful build alone does not establish that the hardware works.

## How to add a machine

1. Open a "New machine" issue (board id, model, `MacNN,N` identifier, SoC, owners, status repository).
2. Create `machines/<board>/machine.yaml` (board directory in lower case: `j716s`, `j614s`). Copy the shape of an existing
   one: `board`, `model`, `identifier`, `soc`, `owners`, `status_repos`, one entry per setup (owner, both firmware
   versions, the kernel/loader/userspace stack), and a `features:` map whose keys come from `schema/features.yaml`.
   Start with every cell you have not run as `untested`, and claims from other people as `kind: reported`.
3. Add yourself to `.github/CODEOWNERS` for `/machines/<board>/`.
4. Run the checks (below) and open a pull request. Entries written by someone else for your machine are opened as
   drafts (`draft: true`) with `kind: reported` and links to your own posts; you convert them when you agree.

## How to record a result

1. Copy `machines/<board>/results/` naming: `YYYY-MM-DD-<slug>.md` (UTC date of the run).
2. Front matter: `date` (UTC, `YYYY-MM-DDTHH:MMZ`), `board`, `setup`, `kind: native`, `build` (a recipe path or an
   inline description), `kernel` (the `uname -r`), `payload_sha256` (full) or `payload_sha256_prefix` with a note,
   `firmware` (both the `os` and `system` firmware fields), `attended` (true when a person was at the machine; say what
   they did), `source` (a permalink into your status repository) and `features` (the feature ids it supports).
3. Body: "What was booted", "Results" (pass, fail or not tested for each action), "Log excerpts (scrubbed)", "Not
   tested". Quote error lines literally and trimmed, never whole journals.
4. Change the cells in `machine.yaml` that the result supports: state, `kind: native`, `evidence` (with the heading
   anchor), `verified` (the date), `upstream`.
5. Run the checks and open a pull request. The board maintainer reviews it; if you are the only maintainer, another
   maintainer approves (a second pair of eyes for the privacy check).

The format follows the omacom/Aurora reporting guide, so a result written here can be pasted into the board's omacom
test-report issue unchanged.

## Local checks

```sh
python3 -m pip install pyyaml pytest          # the only dependencies
python3 tools/validate.py                     # schema + evidence rules (+ stale warnings)
python3 tools/privacy_scan.py                 # whole tree; or pass paths
python3 tools/gen.py                          # regenerate the README tables and site/
python3 tools/gen.py --check                  # fails if the generated output is out of date
python3 tools/pr_status.py --no-fetch         # refresh upstream/status.json without the network
python3 -m pytest -q tests
```

## Privacy

Never in the repository, in any form: serial numbers, ECID, nonces, the boot-security parts of `/chosen`, MAC and
Bluetooth addresses, IP addresses (LAN and VPN included), host names, user names and home paths, Wi-Fi network names
and passphrases, partition UUIDs, account details; Apple firmware, boot objects, per-unit firmware (the N1 Wi-Fi and
Bluetooth image), calibration bytes, NVRAM dumps, raw device trees from a running machine, core dumps, and **full ADT
dumps, even redacted**. Share ADT-derived facts as named properties with values that are the same on every unit of the
board (register addresses, compatible strings, power-domain ids, interrupt numbers). `tools/privacy_scan.py` runs on
every pull request and rejects what it can detect; the reviewer checks the rest. If a leak is merged anyway, the owners
rewrite history and ask GitHub support to purge cached views.

## Governance

- **Owners** (repository admins, from at least two different machines): settings, schema, CI, policy. Initial owners:
  [@rolotrealanis98](https://github.com/rolotrealanis98) (J716s), [@edimoldovan](https://github.com/edimoldovan)
  (J714c), [@TripleU613](https://github.com/TripleU613) and [@betizzel](https://github.com/betizzel) (J714s).
- **Board maintainers** (`.github/CODEOWNERS` for `machines/<board>/`): the people with that machine. A board's data is
  theirs: they can refuse a result they cannot reconcile with their machine, and the disagreement stays visible as two
  setups with different states.
- **Topic maintainers**: whoever does the work in an area, added by an owner on request.
- **Merging**: protected `main`, required checks, squash merge, no force pushes. `machines/<board>/` needs one approval
  from that board's maintainer (or another maintainer when the author is the only one). `topics/` needs one topic
  maintainer or any two board maintainers. `schema/`, `tools/`, `.github/` and this governance text need two owners.
  `upstream/status.json` changes only through the bot's pull request.
- **Changing the rules**: an issue labelled `type:policy`, open at least 7 days, a majority of owners in favour.
- **Inactivity**: a board with no merged change in 60 days is shown as unmaintained (its data stays). An owner inactive
  for 90 days is asked, then moved to emeritus.
- The repository's home can change (see the note at the top); the owners decide it together.

## AI assistance

Contributions made with AI tools are accepted. Every pull request has a human author who has read it and answers for
it. Disclosure is welcome (a sentence in the pull request is enough) but no trailer or tag is required in this
repository. A hardware result must come from a real run on the named machine, never from a tool's summary of what should
have happened.

Code does not live here, but the destinations have their own rules and they apply to anything you send there:
aurora-silicon follows the kernel's `Documentation/process/coding-assistants.rst` (an `Assisted-by:` tag, and only
humans add `Signed-off-by`); omacom repositories do not ask for a tag.

**Nothing from this repository goes to Asahi Linux.** Asahi forbids generative AI in contributions. Treat everything
here as AI-assisted for the purposes of that policy: if you contribute to Asahi Linux, do not copy from this repository.

## Licence

- Documentation and data (`README.md`, `CONTRIBUTING.md`, `topics/`, `machines/`, `builds/`, `upstream/`, `schema/`,
  `site/`): [CC-BY-SA-4.0](LICENSE) (copy also in [`LICENSES/CC-BY-SA-4.0.txt`](LICENSES/CC-BY-SA-4.0.txt)).
- Tools and automation (`tools/`, `tests/`, `.github/workflows/`): [MIT](LICENSES/MIT.txt).
- `CODE_OF_CONDUCT.md` is the Contributor Covenant 2.1 (CC-BY-4.0, from the Contributor Covenant project).

A contribution is offered under the licence of the path it touches. Repositories without a licence are linked, never
copied, unless their author adds a licence or gives written permission in the pull request.

## Contact

Questions and loose notes: GitHub Discussions on this repository. Bugs in a component (kernel, loader, Mesa, packages)
go to that component's repository. Conduct: [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).
