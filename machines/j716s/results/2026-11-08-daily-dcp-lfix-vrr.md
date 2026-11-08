---
date: 2026-11-08T05:28Z
board: J716s
setup: j716s-aurora73
kind: native
build: builds/j716s/daily-dcp-lfix-vrr.yaml
kernel: 7.3.0-gbd53915f2ef1
payload: daily-dcp-lfix-vrr-20261107-7e244836
payload_sha256: 7e244836c80aa6ca83b9794a1db8065bee690fbf024f6df6df3566784712db15
firmware: {os: "27.3 beta 1 (26C5035r), mBoot-20457.60.65.0.1", system: "27.3 beta 1 (26C5035r), mBoot-20457.60.65.0.1"}
attended: false
source: https://github.com/rolotrealanis98/m5pro-linux/blob/70bbffcc160b02903058a7a82a065ef047affdd9/contrib/validated/integration/RESULTS.md#2026-11-08-0528-utc-vrr-round-verifier-pass-on-the-daily-and-on-the-vrr-twin-daily-dcp-lfix-vrr-promoted
features: [display.dcp, display.refresh, display.brightness, gpu.gl]
summary_of: [VRR ROUND]
---

The fixed verifier (`hypr-dcp-verify`, run as root over ssh, finds the user's Hyprland instance itself; every timed pass
requires captured `dcp:iomfb_swap_complete` events) ran on the daily (VRR off) and on the VRR test twin. The VRR twin's
ingredients are identical to the promoted daily's.

## Results

| Payload | Verifier | Detail |
|---|---|---|
| `daily-dcp-lfix` (VRR off) | 19 passed, 0 failed, 3 warnings | Hyprland drives the apple card and renders on `renderD128` (Apple M5 Pro (G17S B1)), scanout buffers 3456x2234 XR24 LINEAR rendered into directly, KMS explicit sync and EGL native fence sync, mode 3456x2234 at 120.000 Hz |
| `daily-dcp-lfix-test-vrr` (`54b4d1c9`, `appledrm.fw27_panel_vrr=1`) | 22 passed, 0 failed, 2 warnings | `vrr_capable` on, aquamarine "capable of vrr", hyprctl `vrrCapable=true`, `misc:vrr=1` active |
| Promoted `daily-dcp-lfix-vrr` | boot pass | booted clean on the primary slot (50 s): `card0` aurora, `card1` apple-drm, DCP session active, Hyprland up |

## 120 Hz pacing

vkcube composited on the daily: 2405 swaps in 20 s, median 120.0/s, p50 8.333 ms, 0 late. On the VRR twin: 2405 swaps,
p50 8.333 ms, p99 8.49 ms, stdev 0.033 ms, 0 late, submit-to-complete 2.7 ms. glmark2 fullscreen: the panel showed 91
frames/s (late compositor frames land at 12.4 ms, three 4.17 ms steps).

## VRR with a 50 fps client

- 50 fps client, VRR off: intervals p50 12.5 ms, whole-refresh multiples {1: 622, 2: 578} (judder).
- 50 fps client, VRR on: intervals p50 20.825 ms, p99 20.92 ms, 0 late, 80 % within 1.5 ms of 20 ms: the panel follows the
  client.
- Kernel: `VRR_ENABLED 0 -> 1`, firmware `adaptive_sync minRR = 0x180000` (24 Hz), `3456x2234@120 Hz DSC=NO VRR=YES`. No
  flip or transaction timeouts, no DCP crash, no faults.

## Promotion

`daily-dcp-lfix-vrr-20261107-7e244836.bin` = `daily-dcp-lfix` + `appledrm.fw27_panel_vrr=1`, daily form. `boot.bin.prev` stays
the previous daily's test twin. The session profile turns `misc:vrr=1` on when the panel offers VRR; the firmware minimum
is 24 Hz.

## Warnings and open items

The idle desktop flipped 247 times in 3 s on the daily boot (something animating right after login; 0 swaps in 3 s on the
twin boots). Mesa skipped glmark2 draws (the AGX backend refused `persp_mul_agx3`; fixed in the unreleased native-GL
patch 0007, see the native GL result). Fullscreen mpv is not direct-scanned (`blockedBy ["CANDIDATE"]`, composited).

## Not tested

Direct scanout, external displays, lid-close sleep on this daily.
