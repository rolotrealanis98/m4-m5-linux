# Thunderbolt and USB4 on the T6050

## Status

- Aurora Silicon's J716c work (aurora-silicon/linux #946) adds Thunderbolt 5 and USB4 on the right USB-C port, including
  a hardware-checked CIO reset sequence.
- **J716s T0 (blocked):** a kernel with USB4/Thunderbolt built in and the ATC1/ATC2 routers, PCIe tunnels, DARTs and NHIs
  in the device tree hung in kernel init: `swapper/0` blocked in `deferred_probe_initcall` -> `flush_work` for over
  1000 s. Userspace and the self-test never ran, and because Linux had taken over the watchdog nothing reset the machine.
- Prime suspect: a router or controller probe that waits forever without the loader's combo-PHY tunables.

## Before anyone tries again

- Add a timeout on that probe path, and use a boot-time watchdog that only Linux's init completion pets.
- Run Thunderbolt payloads attended only, with a power cycle and the macOS recovery path ready.
- Anything a router probe needs from the loader (tunables) should be checked on a USB-only boot first.

## Results and PRs

- J716s: [TB-T0](../../machines/j716s/results/2026-11-08-tb-t0.md).
- PRs: aurora-silicon/linux #946.
