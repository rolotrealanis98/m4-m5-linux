# m1n1 on the T6050

The loader's jobs on the T6050, beyond starting the kernel. Each item says where the code is upstream.

## Bring-up

- **Secondary cores:** start through the existing T6050 sequence once the stub firmware is 27.3 beta 1 or later (see
  [boot-chain](../boot-chain/README.md)). A stage 2 loaded from the ESP needs the RVBAR relay, because the secondaries'
  reset vector stays locked to stage 1: omacom/m1n1 #33.
- **Image size:** keep the raw image under iBoot's size limit (the J716s builds use `MAX_CPUS` 24 and a 0x400000-byte
  plain image).
- **Watchdog:** `m1n1.wdt=keep` leaves the primary watchdog armed for the next stage, so a hang later in the boot still
  resets: omacom/m1n1 #36.

## Hand-offs to Linux

| Hand-off | What m1n1 does | Upstream |
|---|---|---|
| Combo PHY tunables | Fills the per-port PHY tunables from the ADT at boot, so the device tree carries no per-unit values | J716s m1n1 patch 0021 (m5pro-linux), not yet a PR |
| USB-PD controllers | Powers up the Type-C PD controllers into S0 so both ports work | J716s m1n1 patch 0018 (m5pro-linux) |
| N1 (Wi-Fi/Bluetooth) | Keeps a down N1 port enabled with its DART and copies the host tunables, so the kernel can train it; optionally trains the port itself | aurora-silicon/m1n1 #65, omacom/m1n1 #34 |
| GPU | Reserves the firmware regions, sets up the page tables and mailboxes from the ADT, behind an opt-in | omacom/m1n1 #37 |
| Display (DCP) | Hands the running DCP and its framebuffer to the firmware-27 DCP driver, opt-in | omacom/m1n1 #35 |

The hand-offs that touch running coprocessors are opt-in per boot (`chosen.*` variables in the payload), so a payload
without them behaves like a plain loader.

## Results

- J716s: the omacom-stacked m1n1 (PRs #33-#37 after review) boots the daily kernel with the watchdog kept, the RVBAR
  relay and the N1 trained by the loader (m5pro-linux RESULTS.md, "OMACOM-WDT-KEEP-v30 review-fixed"); the daily's own
  loader hands the N1 to the kernel ([K1/K2](../../machines/j716s/results/2026-11-07-k1k2-kernel-trains-n1.md)) and the GPU to the driver
  ([GPU E2b](../../machines/j716s/results/2026-11-07-gpu-e2b-zink.md#e2b-the-gpu-firmware-boots)).
