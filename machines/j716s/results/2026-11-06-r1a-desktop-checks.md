---
date: 2026-11-06T12:00Z
board: J716s
setup: j716s-legacy72
kind: native
build: "asahi-wip 7.2 stack with the omarchy-m5 J716s patches (payload 6d6a402b, battery driver off)"
kernel: 7.2.2-ge1d2d7313745
payload_sha256_prefix: 6d6a402b
firmware: {os: "27.3 beta 1 (26C5035r), mBoot-20457.60.65.0.1", system: "27.3 beta 1 (26C5035r), mBoot-20457.60.65.0.1"}
attended: true
source: https://github.com/rolotrealanis98/m5pro-linux/blob/f8fd6bc71b2688ca70ad7697cd5506fd2ed393da/contrib/validated/integration/RESULTS.md#r1-a-boot-and-desktop-checks-payload-6d6a402b-battery-driver-off
features: [cpu.smp, cpu.cpufreq, input.kbd-backlight, input.trackpad]
---

Round R1-A on the first (7.2) stack, run by Rolando at the machine without the build host. The source notes give the
date of the round but not the time of day; 12:00Z is a placeholder for the time.

## What was booted

Payload `6d6a402b`: kernel `7.2.2-ge1d2d7313745` from the asahi-wip 7.2 tree with the omarchy-m5 J716s patches, the
battery driver held off with an initcall blacklist, m1n1 stage 2 on the ESP. Booted 2 of 2 (the second boot after
`systemctl reboot`).

## Results

| Feature / action | Result | Detail |
|---|---|---|
| 18 CPUs | pass | `nproc` = 18, all up at 0.69 s |
| NVMe | pass | partitions at 12.14 s, no ANS retry |
| Trackpad | pass | `Touch MT ready` at 19.3 s |
| cpufreq governor | pass | `schedutil` on all three policies, max 4308000 |
| cpufreq under load | pass | the loaded cluster reaches 4308000 kHz on cpu1, cpu7 and cpu13 |
| cpufreq idle floor | fail | idle 2964000 / 2964000 / 1620000 kHz instead of the table minimum; later found to be a measurement artifact (R2) |
| Keyboard backlight | pass | levels 0, 32, 255, 0 verified by eye |
| eDP connector | pass | `card0-eDP-1` connected, one mode |
| zram | pass | `zram0`, zstd |
| Restart | pass | comes back on the same payload |

## Keyboard backlight

Set to 0, 32, 255 and 0 from `/sys/class/leds/kbd_backlight`, each level checked by eye. One benign log line:

```
leds_pwm led-controller: failed to read period for kbd_backlight, default to off
```

## cpufreq

`policy0` and `policy6` share a 14-step table 1344000..4308000 kHz; `policy12` has a 16-step table
1308000..4308000 kHz. Governor `schedutil` on all three.

## Not tested

Lid (`evtest` not installed), the battery driver (blacklisted on this payload), OPP offsets (need the build host).
The PMGR `Failed to reach power state` lines for four `b2bd_afc`/`b2bd_afr` domains were seen and not diffed
against an earlier boot.
