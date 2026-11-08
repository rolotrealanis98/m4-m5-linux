---
date: 2026-11-08T08:18Z
board: J716s
setup: j716s-aurora73
kind: native
build: "omacom/m1n1 #33-#37 rebased onto #30 140a36b (m1n1 v1.6.1-430-g64c8ce2) with the daily kernel a0f2f30c967b; self-test on; t6050-n1=4"
kernel: 7.3.0-ga0f2f30c967b
payload: omacom-wdt-keep-r2-20261108-e52ca584
payload_sha256_prefix: e52ca584
firmware: {os: "27.3 beta 1 (26C5035r), mBoot-20457.60.65.0.1", system: "27.3 beta 1 (26C5035r), mBoot-20457.60.65.0.1"}
attended: false
source: https://github.com/rolotrealanis98/m5pro-linux/blob/70bbffcc160b02903058a7a82a065ef047affdd9/contrib/validated/integration/RESULTS.md#2026-11-08-0818-utc-omacom-wdt-keep-r2-stack-on-30-140a36b-pass
features: [cpu.smp, wifi-bt.wifi, wifi-bt.bt]
summary_of: [OMACOM-WDT-KEEP r2]
---

The tip of the omacom m1n1 stack (#36, on #33-#35 and #37, all on edimoldovan's #30 at `140a36b`) on the J716s.

## Results

| Feature / action | Result | Detail |
|---|---|---|
| Boot on the primary slot | pass | 54 s to ssh, first pass |
| CPUs | pass | 18 CPUs |
| N1 | pass | trained by the loader and adopted; Wi-Fi and Bluetooth up |
| Late-heap retention | pass | stage-2 log shows `FDT: retained heap [...]` and `FDT: late heap [...] retained` before the jump |
| Rebase | pass | no conflicts; builds at 0x410000 / 0x420000, 15 warnings as before, 442-443 host tests pass |

The VRR daily was restored afterwards. Branches force-pushed with lease, notes posted on all five PRs.

## Not tested

The GPU and display hand-offs of the stack (they are opt-in and were not armed in this boot); the stack booting without the
stage-1 watchdog (the planned attended sitting).
