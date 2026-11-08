---
date: 2026-11-08T03:03Z
board: J716s
setup: j716s-aurora73
kind: native
build: "daily 36845aa5f650 + DCP 120 Hz v2 + display device tree + VRR pair (opt-in); loader m1n1-plain-n1-dt-gpu-dcp with chosen.m5pro,gpu=1 and chosen.m5,t6050-display=1"
kernel: 7.3.0-gbd53915f2ef1
payload: daily-dcp-test
payload_sha256_prefix: dfe0c6cc
firmware: {os: "27.3 beta 1 (26C5035r), mBoot-20457.60.65.0.1", system: "27.3 beta 1 (26C5035r), mBoot-20457.60.65.0.1"}
attended: false
source: https://github.com/rolotrealanis98/m5pro-linux/blob/f8fd6bc71b2688ca70ad7697cd5506fd2ed393da/contrib/validated/integration/RESULTS.md#2026-11-08-0303-utc-daily-dcp-first-boots-fail-early-panic-fallback-worked
features: [display.dcp]
---

The first daily candidate with the DCP driving the panel.

## Results

| Feature / action | Result | Detail |
|---|---|---|
| Boot of `daily-dcp-test` (`dfe0c6cc`) | fail | error stage 0x30: kernel entered, root never mounted; round trip 214 s against 103 s for a clean boot, so an early panic, not a hang |
| Boot of `daily-dcp-test-vrr` (`3606884e`) | fail | same |
| Fallback | pass | stage 1 booted the previous slot (the daily's test twin) both times; the daily was restored (primary, 59 s to SSH) |

Nothing from the failed boots is on disk (no crash-log region).

## What is new in this combination

The DCP had only booted without the GPU hand-off before. This was the first boot with the m1n1 GPU hand-off, the display
hand-off and both DRM drivers built in together on the daily device tree. Bisect payloads (loader without the display
hand-off; without the GPU variable; the DCP kernel on the daily device tree) were being built.

## Not tested

Everything after the early panic.
