---
date: 2026-11-07T10:50Z
board: J716s
setup: j716s-aurora73
kind: native
build: "WFI test kernel with the daily device tree (series 0059 + 0060: SMC sensors and the right Type-C port)"
kernel: 7.3.0-gf080637018df
payload: wfi-t1-20261107-040d4866
payload_sha256_prefix: 040d4866
firmware: {os: "27.3 beta 1 (26C5035r), mBoot-20457.60.65.0.1", system: "27.3 beta 1 (26C5035r), mBoot-20457.60.65.0.1"}
attended: true
source: https://github.com/rolotrealanis98/m5pro-linux/blob/f8fd6bc71b2688ca70ad7697cd5506fd2ed393da/contrib/validated/integration/RESULTS.md#result-rightport-plug-test-2026-11-07-1050-utc-on-the-wfi-soak-boot-with-the-daily-dtb-rolando-moved-the-hub
features: [usb.host]
---

Rolando moved a USB hub (Ethernet adapter, 2.4 GHz receiver, card reader) from the left-front port to the right port
with the machine running.

## Results

| Feature / action | Result | Detail |
|---|---|---|
| Left-front port | pass | SuperSpeed hub, RTL8153 Ethernet, receiver, card reader (on every boot since R3) |
| Right port host mode | pass | Type-C `port1` switched to data host / power source, VCONN on, partner present |
| Right port speed | pass | the hub enumerated at SuperSpeed Plus Gen 2x1 (10 Gb/s on both tiers) |
| Devices on the right port | pass | keyboard and mouse of the receiver registered; the Ethernet adapter came back and SSH resumed |
| DisplayPort alternate mode | not tested | on either port |
| Charging through the right port | not tested | |

## Log excerpts

A new xHCI pair came up under `382280000.usb` (USB 3.1 Enhanced SuperSpeed). The m1n1 USB-PD S0 setup covers the
right port's controller, and the combo-PHY tunables m1n1 copies from the ADT at boot are right for that port too.

## Not tested

DisplayPort over Type-C, charging in on the right port.
