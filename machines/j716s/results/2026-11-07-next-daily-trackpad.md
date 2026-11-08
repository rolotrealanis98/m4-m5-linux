---
date: 2026-11-07T16:14Z
board: J716s
setup: j716s-aurora73
kind: native
build: "series 3f2bdbc61510 (86 patches), N1-aware m1n1, Wi-Fi chosen lines"
kernel: "series tip 3f2bdbc61510 (release string not recorded in the source)"
payload: next-daily-wifi-20261107-7e285d94
payload_sha256_prefix: 7e285d94
firmware: {os: "27.3 beta 1 (26C5035r), mBoot-20457.60.65.0.1", system: "27.3 beta 1 (26C5035r), mBoot-20457.60.65.0.1"}
attended: true
source: https://github.com/rolotrealanis98/m5pro-linux/blob/f8fd6bc71b2688ca70ad7697cd5506fd2ed393da/contrib/validated/integration/RESULTS.md#result-next-daily-2026-11-07-1614-1621-utc-rolando-watching-the-panel
features: [input.trackpad, audio.speakers, wifi-bt.wifi]
---

Rolando watched the panel and used the trackpad.

## Results

| Feature / action | Result | Detail |
|---|---|---|
| Boot | pass | clean on the panel, primary slot, 18 CPUs |
| Trackpad clicks and haptics | pass | two MTP haptic devices; Rolando: the trackpad clicks give feedback |
| Wi-Fi, Bluetooth | pass | N1 adopted (3 functions), `wlan0` associated, `hci0` |
| Lid settle parameter | pass | `lid_wake_settle_ms` 2000 |
| Netfilter | pass | `nft` works |
| Sound | pass | `AppleJ716` speaker card and `AppleJ716AOP` mic card, -30 dB ceiling, `speakersafetyd` active, PipeWire J716 sink and mic |
| Speaker tone | pass (no faults) | 2 s 1 kHz at -20 dBFS through the sink: `spkr: pwrd reached`, 0 faults; not judged by ear |

The no-self-test twin of this payload was promoted to the daily.

## Not tested

Lid-close sleep on this kernel (it aborted with the adopted N1 port; fixed later the same day, see the lid sleep result).
