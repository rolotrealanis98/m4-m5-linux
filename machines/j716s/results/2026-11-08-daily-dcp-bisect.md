---
date: 2026-11-08T04:23Z
board: J716s
setup: j716s-aurora73
kind: native
build: "daily 36845aa5f650 + DCP 120 Hz v2 + display device tree + VRR pair (opt-in); loader m1n1-plain-n1-dt-gpu-dcp (then the phandle-fix loader), chosen.m5pro,gpu=1 and chosen.m5,t6050-display=1; unattended bisect payloads, one change each"
kernel: 7.3.0-gbd53915f2ef1
payload: daily-dcp-bisect-b1-to-b12
firmware: {os: "27.3 beta 1 (26C5035r), mBoot-20457.60.65.0.1", system: "27.3 beta 1 (26C5035r), mBoot-20457.60.65.0.1"}
attended: false
source: https://github.com/rolotrealanis98/m5pro-linux/blob/70bbffcc160b02903058a7a82a065ef047affdd9/contrib/validated/integration/RESULTS.md#2026-11-08-0410-utc-daily-dcp-bisect-round-3-and-the-root-cause
features: [display.dcp, boot.untethered]
summary_of: [DAILY-DCP bisect rounds 1 and 2, round 3 and the root cause, round 4]
---

The first daily with the DCP driving the panel fell back twice (see the first-boot result). A nine-boot unattended bisect
found why. Every payload differs from the failed twin in one part; stage 1's 150 s watchdog and the A/B fallback were the
safety net, and the daily was restored after each series.

## Results

| Boot | Change | Result |
|---|---|---|
| B2 | no `chosen.m5pro,gpu=1` (display hand-off, kernel N1 training) | fell back, 208 s, stage-1 watchdog |
| B3 | daily-n1k DTB, no display variable | booted, clean (GPU, Wi-Fi, desktop) |
| B1 | loader `n1-dt-gpu` (no display hand-off), twin DTB | booted, clean |
| B5 | B2 with the stage C DTB (dcp9d) | booted, clean: `card1` apple-drm, eDP-2 connected, six 3456x2234 timings, no flip or transaction timeouts, Hyprland up |
| B6, B10, B12, B8 | loader-trained N1; no apcie power-controllers; PCIe statics reverted; no `pwren-gpios` | all fell back, 207-209 s |
| B4 | B2 + the two phandles in the DTB (display hand-off, no GPU) | booted, clean, 50 s: `card1` apple-drm, eDP-2, six timings, no timeouts, Hyprland up |

## Root cause

`dt_set_display_t6050()` in the loader re-finds the display nodes by phandle and bails with "DCP: T6050: a display node has
no phandle" when `dcp` or `display-subsystem` has none. dtc emits a phandle only for nodes some property references;
the in-tree J716s DT labels both nodes but only extends them (`&dcp { ... }`), so the in-tree DTB has no phandle on
either (the stage C DTB, built differently, has 0xd3 and 0xd4). The bail makes `kboot_prepare_dt()` fail, stage 2
prints "Failed to prepare FDT!" and drops into the proxy; with no host attached nothing feeds the watchdog, and the
stage-1 150 s dog resets the machine. That fits every boot: with the display hand-off and the in-tree DTB everything
fell back; without the hand-off (B1, B3) or on the stage C DTB (B5) everything booted.

## Fix

A loader patch gives any display node without a phandle a new one (highest offset first); the same change is pushed to
omacom/m1n1 #35. With the two phandles in the DTB the DCP boots on the in-tree device tree (B4 above).

## Not tested

GPU and DCP together on this fix (the next result). No console capture exists for the first fallbacks: iBoot clears the
crash-log region on every boot.
