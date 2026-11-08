---
date: 2026-11-07T21:35Z
board: J716s
setup: j716s-aurora73
kind: native
build: "GPU tree + DRM_APPLE with the 27.3 method table and swap layout (#1174), m1n1 n1-warm-gpu-dcp with chosen.m5,t6050-display=1, display nodes with the internal panel's bw-scratch"
kernel: 7.3.0-dcp-g3671d907d570
payload: dcpc-20261107-9ec63d9a
payload_sha256_prefix: 9ec63d9a
firmware: {os: "27.3 beta 1 (26C5035r), mBoot-20457.60.65.0.1", system: "27.3 beta 1 (26C5035r), mBoot-20457.60.65.0.1"}
attended: false
source: https://github.com/rolotrealanis98/m5pro-linux/blob/f8fd6bc71b2688ca70ad7697cd5506fd2ed393da/contrib/validated/integration/RESULTS.md#display-stage-c-the-dcp-drives-the-internal-panel-2026-11-07-2135-utc--pass-unattended-remote-checks
features: [display.dcp]
---

Stage C of the display bring-up, checked remotely; Rolando later saw the console on the panel.

## Results

| Feature / action | Result | Detail |
|---|---|---|
| Boot | pass | primary slot first pass, 75 s to SSH, Wi-Fi up |
| Loader hand-off | pass | the DCP, its mailbox and DARTs and the display subsystem handed over, firmware-compat 27.3.0 |
| DCP driver | pass | firmware pipeline started, `DCP booted`, simpledrm replaced by `apple-drm` |
| Connector | pass | `card1-eDP-2` connected and enabled, six 3456x2234 modes |
| Console through the DCP | pass | fbcon moved to eDP-2 and kept printing for the whole boot; 8 atomic commits |
| Swap cadence | not measured | tracing was compiled out in this kernel |
| Brightness | not tested | the "50 % write" wrote the current value (no-op) |

## Log excerpts

```
live DCP DMA resources retained until reboot
negotiating RTKit with the running DCP
switch to normal mode succeeded
dcp_hotplug() connected:1 nr_modes:6
DCP booted
```

No `DCP has crashed`, `swap failed`, `Incompatible devicetree` or timeout lines; 0 fault lines. The mode set was a
no-op for the firmware (the 120 Hz timing iBoot left running). The firmware's complaint about an undeclared clock
provider was fixed in the next device tree (see the 2026-11-08 DCP-120 result).

## Not tested

Swap cadence, brightness, VRR (all in the DCP-120 runs), the DCP together with the GPU hand-off in a daily.
