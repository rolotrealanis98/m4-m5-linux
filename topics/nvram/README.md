# NVRAM on the T6050

- The boot NOR is on the qspi controller. With the controller and a `jedec,spi-nor` flash node enabled, and a fixed
  partition `nvram` at offset 0x700000, size 0xc0000, Linux exposes the NVRAM as an MTD device.
- On the J716s the 768 KiB partition reads back fully through `/dev/mtd2ro` and parses read-only: 12 banks of 64 KiB
  with consecutive generations, variable names matching what macOS shows.
- An NVRAM dump carries per-unit values and tokens: never commit one, not even partly. Quote variable names only.
- Writing is the useful next step (for example choosing the next boot volume from Linux) and is planned as an attended
  sitting with a write-verified driver.

## Results

- J716s: [NVRAM read-only](../../machines/j716s/results/2026-11-07-nvram-ro.md), [in the daily](../../machines/j716s/results/2026-11-07-daily-n1k.md#results).
