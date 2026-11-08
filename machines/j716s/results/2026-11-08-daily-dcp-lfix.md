---
date: 2026-11-08T04:53Z
board: J716s
setup: j716s-aurora73
kind: native
build: "builds/j716s/daily-dcp-lfix-vrr.yaml (this result is the VRR-off form, daily-dcp-lfix)"
kernel: 7.3.0-gbd53915f2ef1
payload: daily-dcp-lfix-20261107-689facad
payload_sha256: 689facad94cb4aafa813ed888c7d0e580142bab050cc99acbbc6c38fdc7b12da
firmware: {os: "27.3 beta 1 (26C5035r), mBoot-20457.60.65.0.1", system: "27.3 beta 1 (26C5035r), mBoot-20457.60.65.0.1"}
attended: false
source: https://github.com/rolotrealanis98/m5pro-linux/blob/70bbffcc160b02903058a7a82a065ef047affdd9/contrib/validated/integration/RESULTS.md#2026-11-08-0453-utc-daily-dcp-promoted-daily-dcp-lfix-20261107-689facadbin-is-the-daily
features: [display.dcp, display.brightness, gpu.gl, desktop.session]
summary_of: [DAILY-DCP VRR twin, DCP session measurements, DAILY-DCP PROMOTED]
---

The DCP drives the internal panel, the GPU renders into the scanout buffers, in the daily. Unattended; the promotion boot
was a plain reboot on the primary slot.

## Results

| Feature / action | Result | Detail |
|---|---|---|
| Promotion boot | pass | `card0` aurora, `card1` apple-drm with eDP-2 connected, no flip or transaction timeouts, no DCP crash, no faults |
| Desktop on the DCP | pass | two-card Hyprland session (`AQ_DRM_DEVICES=/dev/dri/card1`, render node `renderD128`) |
| Wi-Fi, Bluetooth | pass | Wi-Fi connected, `hci0` |
| Backlight | pass | backlight 300/600 and writes reach the panel (read back through the backlight class; a by-eye note is not in the source) |
| Rollback | pass | `boot.bin.prev` = the previous daily's test twin (`5c74c66c`), reaches the network |

## GPU and DCP together (the VRR twin boot)

`daily-dcp-phfix-test-vrr` (kernel `7.3.0-gbd53915f2ef1`, phandle-fixed DTB, `chosen.m5pro,gpu=1` +
`chosen.m5,t6050-display=1`, `appledrm.fw27_panel_vrr=1`) booted cleanly (50 s): `card0` aurora (GPU), `card1` apple-drm
(DCP, eDP-2 connected, six 3456x2234 timings), `renderD128`, no flip or transaction timeouts, no DCP crash, no faults,
Wi-Fi and Bluetooth up. glmark2 inside the session reported `GL_RENDERER Apple M5 Pro (G17S B1)` at 911 FPS: the first
desktop with GPU rendering and DCP scanout on this machine.

## Session measurements

- Hyprland drives `/dev/dri/card1` (apple-drm) and renders on `renderD128` with the native GL tree; scanout buffers
  3456x2234 XR24 LINEAR, rendered into directly (no copy); explicit sync with timeline syncobjs on both cards; all six
  panel modes listed, 120 Hz preferred.
- VRR was on from the profile (`misc:vrr=1`): kernel log at 10.3 s "VRR_ENABLED 1", firmware minimum refresh 24 Hz,
  "3456x2234@120 Hz DSC=NO VRR=YES"; no DCP or GPU errors.
- 120 Hz pacing, vkcube composited: 2397 swaps in 20 s (119-120/s), interval typical 8.334 ms, p99 8.51 ms, max
  12.45 ms; 2396 of 2397 intervals one refresh; submit-to-complete 2.9 ms (p99 3.0). Idle desktop: 0 swaps in 3 s.

## Counted restart on the first write

The first write-and-reboot of the new daily was counted as a failed restart (first pass, 55 s; the new file was never
read) and stage 1 booted the previous slot; a plain reboot 30 s later booted the new daily. This is the intermittent
counted-restart class of the boot-safety result (clean boots in the same runner measure 49-51 s). A 55 s fallback
earlier the same night was first read as a GPU + DCP panic and corrected to this class.

## Not tested

Direct scanout of fullscreen clients, the 50 fps VRR test (next result), a brightness check by eye, lid-close sleep
with the DCP.
