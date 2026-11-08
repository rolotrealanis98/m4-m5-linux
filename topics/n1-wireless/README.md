# N1 Wi-Fi and Bluetooth on the T6050

The N1 is the Wi-Fi/Bluetooth module on PCIe port 0 (functions `106b:1900`, `106b:1902`, `106b:1903`). Its firmware
is personalised per unit and is never published here.

## What works

- **The kernel trains the port itself.** When the boot loader leaves port 0 down (but enabled, with its DART and the host
  tunables copied from the ADT), pcie-apple trains it cold: `port 0: trained by Linux, the boot loader left it down`.
  The cold train, the host tunables and the DART availability commits are edimoldovan's (J714c); the J716s adds a 250 ms
  power-line reset for a warm N1 and its own SMC GPIO template for the power line. Native on the J716s, reported on the
  J714c, so it is a candidate for "reproduced" once the J714c entry is confirmed.
- **Adoption:** a port the loader already trained is adopted as it is (aurora-silicon/linux #937).
- **Restart with the link up:** the pcie-apple shutdown puts each adopted port back into its cold state (bridge decoding
  off, PME_Turn_Off and L2, PERST# asserted, clocks stopped), so the next boot trains it again.
- **ASPM:** L0s and L1 are stripped on the adopted root port; without that both boards froze 20-40 s after boot. No
  `pcie_aspm=off` boot flag is needed.
- **Suspend-to-idle:** the adopted link is kept up through s2idle; before that fix pcie-apple refused to suspend
  (`-EBUSY`) and lid sleep aborted.
- iwd needs the kernel crypto user APIs (`CRYPTO_USER_API_HASH`, `CRYPTO_USER_API_SKCIPHER`, `KEY_DH_OPERATIONS`);
  wpa_supplicant works without them.

## Open

- 6 GHz: reported working on the J714c; the J716s unit's regulatory list has no 6 GHz entries.
- Bluetooth pairing has not been recorded on the J716s; the controller scans.
- J714s: not working yet on either setup.

## Results and PRs

- J716s: [K1/K2, the kernel trains the port](../../machines/j716s/results/2026-11-07-k1k2-kernel-trains-n1.md),
  [first bring-up, association and restarts](../../machines/j716s/results/2026-11-07-n1-wifi-bring-up.md),
  [lid sleep with the N1 adopted](../../machines/j716s/results/2026-11-07-lid-sleep-n1.md#n1-sleep), [the daily](../../machines/j716s/results/2026-11-07-daily-n1k.md#wi-fi).
- PRs: aurora-silicon/linux #1182 (driver half) and #1183 (device-tree half), #937 (adoption), #938 (N1 Wi-Fi/Bluetooth on
  bare-metal T6050); aurora-silicon/m1n1 #65 and omacom/m1n1 #34 (loader-side training, now optional).
