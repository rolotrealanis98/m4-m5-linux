---
date: 2026-11-07T23:37Z
board: J716s
setup: j716s-aurora73
kind: native
build: "the daily kernel with the review-fixed omacom loader stack, then the daily; A/B stage 1 with a 150 s watchdog"
kernel: 7.3.0-ga0f2f30c967b
payload: omacom-wdt-keep-20261107-15618a15
payload_sha256_prefix: 15618a15
firmware: {os: "27.3 beta 1 (26C5035r), mBoot-20457.60.65.0.1", system: "27.3 beta 1 (26C5035r), mBoot-20457.60.65.0.1"}
attended: false
source: https://github.com/rolotrealanis98/m5pro-linux/blob/f8fd6bc71b2688ca70ad7697cd5506fd2ed393da/contrib/validated/integration/RESULTS.md#restart-exp4-a-disk-write-burst-right-before-the-reboot-reproduces-the-failure-without-any-esp-write-2026-11-07-2337-utc
features: [boot.safety]
summary_of: [First-boot fallback root cause, CRASHLOG-PRAM, RESTART-EXP2, RESTART-EXP3, RESTART-EXP4]
---

What makes unattended testing safe on the J716s, and the one rule it needs.

## The safety net

Two-stage m1n1 with an A/B stage 1: after a failed boot (counted by iBoot's boot-failure counter) stage 1 boots the
previous payload; a 150 s watchdog covers a hang before Linux takes it over; test payloads revert themselves when the
network does not come up within 90 s. Over 7 November it brought the machine back from every failed test payload
without a person, except the Thunderbolt hang (see that result) and a loader that disables the watchdog (never put on
the boot slot unattended).

## RESTART-EXP4: the cause of "the first boot of a fresh payload falls back"

Three times: `dd if=/dev/zero of=/root/burst bs=1M count=70 conv=fsync` on the ext4 root, then `systemctl reboot`
within 1 s, no ESP write at all. Arm 1: `fallback-after-failure`, error stage 0x30 (the next boot of the unchanged
payload died in early Linux and the twin booted). Arms 2 and 3: clean. Then three times: rewrite the same payload to
the ESP, wait 60 s, reboot: all clean.

Conclusion: rebooting while the SSD is still busy after a write burst makes the next boot fail early (0x30) or counts
the restart as a failure (0x00), independent of the FAT ESP. **Rule: 60 s of idle after any large write before a
reboot.** With the settle: 9 of 9 clean that day; with a ~1 s gap, 5 of 14 failed. The ESP write helper defaults to the
60 s settle.

## RESTART-EXP2 and EXP3

Plain `systemctl reboot` cycles without a write, from the power-kernel and the omacom-loader sessions: 3 of 3 and 3 of
3 clean (primary slot).

## CRASHLOG-PRAM: no RAM-backed crash log

A ramoops region carved from iBoot's panic-log region registered, but both a warm reboot and a deliberate panic left
the store empty on the next boot: iBoot consumes and clears that region and the DRAM is zeroed. Evidence from a frozen
boot has to come from outside the machine (netconsole).

## Not tested

The stage-1 change that marks boot stages so a counted restart boots the primary (built, waiting for an attended
sitting).
