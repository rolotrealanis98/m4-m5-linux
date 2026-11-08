# Boot chain on the T6050 (M5 Pro and M5 Max)

What it takes to start Linux on a T6050 MacBook Pro, and how to get back when a boot fails. Machine-specific results are
linked at the end; the J716s is the only board with native results in this repository so far.

## Stub firmware decides how many cores come up

- macOS 27.3 beta 1 (26C5035r) fixed the single-core limit for custom raw boot objects on M5 Pro, M5 Max and M5 Ultra
  (Apple's release notes, mBoot resolved issues). Before it, secondary cores power up but never start.
- The second stage that starts the cores comes from the **stub's** restore bundle (`/chosen/firmware-version`), not
  from the main macOS volume (`/chosen/system-firmware-version`). Updating macOS alone is not enough: the stub has to
  be recreated (or updated in place, which worked on the J714c) from 27.3 beta 1 or later. Both fields then read
  `mBoot-20457.60.65.0.1`.
- With that firmware, m1n1's existing T6050 start sequence brings up every core. Reported on three boards: J716s
  (18 cores, native here), J714c (18) and J714s (15, a binned part).
- Firmware version and the kernel/loader work are separate questions: the GPU and display interfaces are keyed by
  firmware version, and 27.2 and 27.3 use the same layouts except one GPU data word (see [gpu](../gpu/README.md)).

## Loader layout used on the J716s

- **Stage 1** on the boot slot (m1n1, CHAINLOADING build) with an A/B fallback: when iBoot's boot-failure counter is
  set, it boots the previous payload; a 150 s watchdog covers a hang before Linux takes it over.
- **Stage 2** on the ESP: one file holding m1n1, the `chosen` lines, the kernel, the device tree and the initramfs.
  Stage 2 has to relocate above the secondary-only CTRR window and, because the secondaries' RVBAR stays locked to the
  stage-1 base, it installs a small relay there (upstream as omacom/m1n1 #33).
- **Test payloads** revert themselves when the network does not come up within 90 s.

The Omarchy installer's chain (stage 1, stage 2, U-Boot, Limine, an EFI kernel) is what edimoldovan's J714c boots from
disk (omacom/m1n1 #30); on the J716s it is built and waits for an attended cold start.

## Rules that save a machine

- **Wait 60 s after any large write before rebooting.** Rebooting while the SSD is still busy after a write burst makes
  the next boot fail early or counts the restart as a failure, whether the write went to the ESP or to the root
  filesystem. With the settle, 9 of 9 restarts were clean on the J716s; with a 1 s gap, 5 of 14 failed.
- Never put a loader that disables the stage-1 watchdog on the boot slot unattended: a stop in the m1n1 proxy is not
  counted as a failed boot, so the fallback never runs.
- A hang inside Linux init after Linux owns the watchdog is not caught either (it happened with the Thunderbolt test,
  see [thunderbolt](../thunderbolt/README.md)).
- RAM-backed crash logs do not survive a reset on the J716s (iBoot clears its panic region and the DRAM is zeroed);
  capture from outside the machine (netconsole).

## Results and PRs

- J716s: [untethered daily](../../machines/j716s/results/2026-11-07-daily-n1k.md#results),
  [boot safety and the settle rule](../../machines/j716s/results/2026-11-07-boot-safety-settle.md),
  [Omarchy chain status](../../machines/j716s/machine.yaml).
- J714c and J714s claims: [machines/j714c](../../machines/j714c/machine.yaml), [machines/j714s](../../machines/j714s/machine.yaml).
- PRs: omacom/m1n1 #30 (J714c disk boot), #33 (RVBAR relay), #36 (`m1n1.wdt=keep`); omacom/linux-aurora #404, #413.
