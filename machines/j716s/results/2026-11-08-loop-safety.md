---
date: 2026-11-08T05:10Z
board: J716s
setup: j716s-aurora73
kind: native
build: "twins of next-daily-wifi (loader-trained N1, chosen.m5pro,n1=4) on kernel a0f2f30c967b with the initramfs watchdog opener; v1 at 03:22 UTC, v2 at 05:10 UTC"
kernel: 7.3.0-ga0f2f30c967b
payload: "wdt2-opener and wdt2-noopener twins (v2); wdt-opener 2daadc5b (v1)"
firmware: {os: "27.3 beta 1 (26C5035r), mBoot-20457.60.65.0.1", system: "27.3 beta 1 (26C5035r), mBoot-20457.60.65.0.1"}
attended: false
source: https://github.com/rolotrealanis98/m5pro-linux/blob/70bbffcc160b02903058a7a82a065ef047affdd9/contrib/validated/integration/RESULTS.md#2026-11-08-0510-utc-loop-safety-v2-negative-pass-positive-hand-over-pass-systemd-now-owns-the-watchdog-on-the-daily
features: [boot.loop-safety, boot.safety]
summary_of: [LOOP-SAFETY watchdog twins v1, LOOP-SAFETY v2]
---

Why: the Thunderbolt T0 kernel hung in init with the watchdog already handed to Linux, so the machine never reset (see
the T0 result). Test payloads now carry `watchdog.open_timeout=300` and an initramfs opener that pets `/dev/watchdog0`
until userspace takes over; a kernel that reaches userspace but never opens the device is reset by the core and stage 1
falls back. Error stage cleared before each boot, `ESP_SETTLE=120`.

## Results

| Test | Result | Detail |
|---|---|---|
| Negative `wdt2-noopener` (`m5.wdt=off`, `watchdog.open_timeout=120`, drop-in removed first) | pass | the twin ran (its journal is on disk) and wrote the stage marks 0x31 (initramfs), 0x33 (root) and 0x34 (network up, 8.5 s); the kernel stopped feeding the dog at the 120 s open timeout and it bit about 150 s in; stage 1 fell back to prev with error stage 0x34 (fallback kernel 192 s after the reboot, the "apple_wdt bite" band) |
| Positive `wdt2-opener` (`watchdog.open_timeout=300`) | pass (hand-over) | `m5-wdt` lines in order: initramfs reached, `/dev/watchdog0` opened and petted, `m5pro-watchdog.conf` installed, device released, "systemd opens it next"; systemd 1.4 s: "Using hardware watchdog /dev/watchdog0", `RuntimeWatchdogUSec=1min` |
| Positive run length | partial | the twin ran 100 s with PID 1 feeding the dog (no reset) until its own self-test reverted it; the 400 s criterion was not reached on this boot (v1 reached it with the petter) |

A boot that reaches userspace but never opens the device is reset and recovered, with the stage of death recorded.

## v1 (03:22 UTC), for the record

Positive `wdt-opener` (`2daadc5b`, `watchdog.open_timeout=300`, initramfs opener): booted, m5-selftest "network OK", up past
400 s with no reset, clean `systemctl reboot` back on the primary slot. The hand-over to systemd did not happen: no
`m5pro-watchdog.conf` drop-in, `RuntimeWatchdogUSec=0`, "Failed to open watchdog device /dev/watchdog0: Device or resource
busy" at shutdown and the kernel "watchdog did not stop!". v2 fixed this (the pre-switch_root block, kmsg logging, the
0x31 stage mark). The v1 negative twin was inconclusive (the fallback came in the 75-169 s band, with no journal of the
twin) and was rerun in v2 with the stage marks.

## Side effect (intended)

The drop-in now lives on the shared root, so the daily runs with `RuntimeWatchdogSec=60`: a PID 1 stall of over 60 s resets
the machine. s2idle is handled by the watchdog core's PM notifier and `apple_wdt` suspend/resume.

## Not tested

A lid-close sleep with systemd owning the watchdog (the case that matters on the daily; attended). The positive twin's
own self-test failed once (`ping` of the fixed check address failed although wlan0 had associated at 6.5 s); one
occurrence, not understood, unrelated to the watchdog.
