---
date: 2026-11-07T14:40Z
board: J716s
setup: j716s-aurora73
kind: native
build: "series tip + kernel crypto for iwd (0065) + netfilter, policy routing and WireGuard built in (0064)"
kernel: 7.3.0-g91812cddaf1c
payload: "bisect payloads C and D (their hashes are not recorded in the source)"
firmware: {os: "27.3 beta 1 (26C5035r), mBoot-20457.60.65.0.1", system: "27.3 beta 1 (26C5035r), mBoot-20457.60.65.0.1"}
attended: false
source: https://github.com/rolotrealanis98/m5pro-linux/blob/f8fd6bc71b2688ca70ad7697cd5506fd2ed393da/contrib/validated/integration/RESULTS.md#result-lid-daily-promotion--bisect-c-and-d-2026-11-07-1440-1452-utc-loop-nobody-at-the-machine
features: [net.netfilter]
---

Bisect payloads C and D of the next daily, nobody at the machine. Kernel D is the one with netfilter; it and the combined
kernel that followed (`7.3.0-g24e777afc7f6`, 0063 + 0064 + 0065) both boot.

## Results

| Kernel | Boots | `nft` | `ip rule` | iwd |
|---|---|---|---|---|
| C `7.3.0-ga2518bd52a46` (+0065 crypto) | yes | ok | unsupported (expected) | active |
| D `7.3.0-g91812cddaf1c` (+0064 netfilter) | yes | ok | lists the local table | active |
| combined `7.3.0-g24e777afc7f6` | yes, 169 s to SSH, primary slot | ok | ok | active |

These patches are part of the 87-patch series every daily since 17:00 UTC carries.

## Not tested

A WireGuard tunnel, a firewall front end (ufw) on this kernel.
