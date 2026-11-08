---
date: 2026-11-07T13:44Z
board: J716s
setup: j716s-aurora73
kind: native
build: "series and WFI kernels with the loader-trained N1 (m1n1 n1-smc, later n1-warm), initramfs carrying the unit's N1 firmware (not published), pcie_aspm=off"
kernel: 7.3.0-g4f630b11270d
payload: w3b-aspmoff-20261107-009a839e
payload_sha256_prefix: 009a839e
firmware: {os: "27.3 beta 1 (26C5035r), mBoot-20457.60.65.0.1", system: "27.3 beta 1 (26C5035r), mBoot-20457.60.65.0.1"}
attended: true
source: https://github.com/rolotrealanis98/m5pro-linux/blob/f8fd6bc71b2688ca70ad7697cd5506fd2ed393da/contrib/validated/integration/RESULTS.md#result-w3b-2026-11-07-1344-utc-cold-start-by-rolando-wi-fi-and-bluetooth-come-up
features: [wifi-bt.wifi, wifi-bt.bt]
summary_of: [W3b, DAILY-WIFI-T1, W4]
---

The first Wi-Fi and Bluetooth bring-up on the J716s, with m1n1 training the N1's PCIe port and the kernel adopting it.
Three runs: W3b (13:44 UTC, cold start by Rolando), DAILY-WIFI-T1 (14:00 UTC, nobody at the machine) and W4 (15:37 UTC,
restarts with the link in use). The current daily trains the port in the kernel instead (see the K1/K2 result).

## W3b

```
pcie-t6050: port 0 link Gen1 x1
endpoint 01:00.0 is 0x1900106b
apple_centauri: enabling device
port 0: link retrained after a root-port reset
Wi-Fi firmware channels: 2.4 GHz 13, 5 GHz 25, 6 GHz 0 (38 entries)
```

Functions `[106b:1900]`, `[106b:1902]` and `[106b:1903]` enumerate; `wlan0` (phy0, managed) and `hci0`
(Bluetooth version 17) register, rfkill clear; up past 123 s with ASPM off. Radio check on the same boot: `iw dev wlan0
scan` lists 55 BSS entries (33 networks) on 2.4 and 5 GHz; `btmgmt find` for 8 s finds 36 devices.

## DAILY-WIFI-T1

`wpa_supplicant` with a configuration written by `wpa_passphrase` (the passphrase is only on the machine's root):
`wpa_state=COMPLETED`, WPA2-PSK, 5 GHz (5200 MHz), signal -30 dBm, DHCPv4 lease and gateway from the home router,
3 of 3 pings answered over `wlan0` (17 ms average). Bluetooth controller up.

## W4

Three `systemctl reboot` cycles with `wlan0` associated and a ping running: all three back on the primary slot, N1
adopted, `wlan0` associated again. The pcie-apple shutdown that parks the adopted port (edimoldovan's, from the J714c)
is what makes the restart work.

## Not tested

6 GHz (no 6 GHz entries in this regulatory list), Bluetooth pairing, throughput.
