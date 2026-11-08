---
date: 2026-11-07T21:27Z
board: J716s
setup: j716s-aurora73
kind: native
build: "87-patch series + kernel-side N1 training (wireless 0004-0010: cold train, host tunables, DART availability, 250 ms warm-N1 power reset, J716s gP13 template and DT); m1n1 n1-dt (port left down and enabled, host tunables copied)"
kernel: 7.3.0-g50d99dcea7b4
payload: n1kernel-k1-20261107-c62b1ca5
payload_sha256_prefix: c62b1ca5
firmware: {os: "27.3 beta 1 (26C5035r), mBoot-20457.60.65.0.1", system: "27.3 beta 1 (26C5035r), mBoot-20457.60.65.0.1"}
attended: false
source: https://github.com/rolotrealanis98/m5pro-linux/blob/f8fd6bc71b2688ca70ad7697cd5506fd2ed393da/contrib/validated/integration/RESULTS.md#k1k2-the-kernel-trains-the-n1-port-itself-2026-11-07-2127-utc--pass
features: [wifi-bt.wifi, wifi-bt.bt]
---

## What was booted

K1: the loader leaves the N1 port down (no `chosen.m5pro,n1` variable) and the kernel trains it. K2 (payload
`n1kernel-k2-20261107-96afa462`): the loader trains the port as before and the kernel adopts it.

## Results

| Run | Result | Detail |
|---|---|---|
| K1 | pass | the kernel trains the port, all three functions enumerate, Wi-Fi connected, Bluetooth up, 77 s to SSH, primary slot |
| K1, warm restart with `wlan0` in use | pass | trained again by the kernel |
| K2 (loader-trained, adopted) | pass | `Link down`, then `link retrained after a root-port reset`; Wi-Fi and Bluetooth up |
| Restore of the daily | pass | primary slot first pass |

## Log excerpts

```
n1: port 0 not up: root port and DART okay
pcie-apple 1cb0000000.pcie: port 0: trained by Linux, the boot loader left it down
port 0: link retrained after a root-port reset
```

Functions 106b:1900, 106b:1902 and 106b:1903. One line matched the fault filter on each boot: the benign nvme
`PANICLOG not yet written` RTKit syslog line (same count on the daily).

## Not tested

6 GHz, Bluetooth pairing, throughput.
