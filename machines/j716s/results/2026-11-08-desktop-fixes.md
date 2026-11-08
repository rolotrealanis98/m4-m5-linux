---
date: 2026-11-08T09:55Z
board: J716s
setup: j716s-aurora73
kind: native
build: builds/j716s/daily-dcp-lfix-vrr.yaml
kernel: 7.3.0-gbd53915f2ef1
payload: daily-dcp-lfix-vrr-20261107-7e244836
payload_sha256_prefix: 7e244836
firmware: {os: "27.3 beta 1 (26C5035r), mBoot-20457.60.65.0.1", system: "27.3 beta 1 (26C5035r), mBoot-20457.60.65.0.1"}
attended: true
source: https://github.com/rolotrealanis98/m5pro-linux/blob/70bbffcc160b02903058a7a82a065ef047affdd9/contrib/validated/integration/RESULTS.md#2026-11-08-0955-utc-desktop-fixes-with-rolando-at-the-machine-vrr-dcp-daily
features: [audio.speakers, desktop.omarchy, desktop.session, gpu.gl-native, input.trackpad]
summary_of: [desktop fixes with Rolando at the machine]
---

Rolando at the machine, on the VRR DCP daily with Omarchy 4.5.0.

## Results

| Feature / action | Result | Detail |
|---|---|---|
| Speakers | pass | the chain was linked (bring-up filter sink -> hidden RawSpeakers, 6 channels) but the raw speaker route was stored at 2.7 % in WirePlumber's state, the sink at 48 %, under the kernel -30 dB ceiling; with the route at 100 %, the sink at 60 % and the speaker sink as the default, Rolando heard the test tone. The ceiling stays until the listening test |
| Wallpaper | pass after a fix | Omarchy 4.5's shell reads the image size with `magick identify`; `imagemagick` was not installed; installed, shell restarted (`omarchy-restart-shell`) |
| Terminals on the native GL driver | fail | black windows and repeated "app failure" notifications: `G17G Gallium could not build the native fragment program`, draws "outside the native profile" dropped |
| Desktop GL back on zink | pass | `session.env.zink` copied over `session.env` (`session.env.native-20261108` kept), desktop restarted: Hyprland on the DCP session with zink, Alacritty clean |
| Trackpad feel | pass | Rolando confirmed the feel of the trackpad at the machine on 2026-11-08 (a person's statement; no log lines, the source records the confirmation outside RESULTS.md) |

## Terminals on the native GL driver

The native Gallium driver cannot build Alacritty's fragment program (the text shader's uniform layout puts a sysval range
at an odd uniform half, and the M5 program builder only accepts dword-aligned ranges). Native GL stays the A/B variant;
the analysis, fixes (native patches 0006-0008) and an A/B plan for a second tree are in the native GL issue.

## Package fill

Two packages that Omarchy's shell needs were not pulled in by Omarchy's own dependencies on this aarch64 root:
`imagemagick` (wallpaper size) and `qt6-imageformats` (the Qt webp plugin; the wallpaper layer was blank without it, fixed
2026-11-07). Both were installed by hand; the dependency lists are an upstream packaging item.

## Not tested

The Omarchy menu, lock screen and first-run flow on this daily (not logged); NetworkManager (not enabled on purpose, the
network widget shows offline); the ~110 optional Omarchy apps (held back).
