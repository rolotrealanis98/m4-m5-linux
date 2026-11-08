---
date: 2026-11-07T10:08Z
board: J716s
setup: j716s-aurora73
kind: native
build: "series kernel + T6050 WFI override + PM_DEBUG, the daily device tree, battery on"
kernel: 7.3.0-gf080637018df
payload: wfi-t1-20261107-040d4866
payload_sha256_prefix: 040d4866
firmware: {os: "27.3 beta 1 (26C5035r), mBoot-20457.60.65.0.1", system: "27.3 beta 1 (26C5035r), mBoot-20457.60.65.0.1"}
attended: true
source: https://github.com/rolotrealanis98/m5pro-linux/blob/f8fd6bc71b2688ca70ad7697cd5506fd2ed393da/contrib/validated/integration/RESULTS.md#result-wfi-t1-2026-11-07-1008-utc-self-revert-loop--ab-stage-1-nobody-at-the-machine
features: [cpu.idle, sleep.s2idle]
summary_of: [WFI-T1, WFI soak + SLEEP S1-S4]
---

Two runs on the same payload: the first boot (10:08 UTC, nobody at the machine) and a 76-minute boot with a soak and
the sleep steps (10:26-11:42 UTC, Rolando at the machine for the real suspend).

## What was booted

Kernel `7.3.0-gf080637018df`: the series plus the patch that keeps T6050 cores idling in WFI even though m1n1 appends
`idle=nop` (upstream as aurora-silicon/linux #1152), with `kvm-arm.wfi_trap_policy=trap`.

## WFI-T1

```
Apple: preserving registers across WFI
Apple: idling in WFI, ignoring idle=nop
```

cpuidle driver `apple_idle`; CPU 0 spent 209 s of its first 211 s in the WFI state (38814 entries). Idle power on the
charger (SMC total system power, read moments apart at the same idle): 16.4 W with the spinning idle, 8.6 W with WFI
(heatpipe 5.7 W to 1.9 W).

## Soak

56 minutes: no RCU stall, Oops or SError; all 18 cores pass a floating-point consistency run; CPU 0 had 409k WFI
entries; idle on the charger 9.8 W.

## Sleep steps

| Step | Result | Detail |
|---|---|---|
| S1 freezer | pass | 5 s |
| S2 `pm_test=devices` | pass | 7 s; USB (22 devices), Ethernet and trackpad back |
| S3 `pm_test=platform` | pass | 7 s; same recovery |
| S4 real s2idle, wake on the power button | pass | see below |

```
Timekeeping suspended for 346.641 seconds
```

`suspend_stats` success 4 / fail 0; USB, Ethernet (carrier back) and battery after resume.

## Not tested

Power while asleep on battery, lid-close wake (see the lid sleep result), repeated cycles in one boot, sleep with the
right Type-C port in use.
