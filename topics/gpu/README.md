# GPU on the T6050 (G17S in the M5 Pro, G17C in the M5 Max)

## Firmware interface

- The GPU firmware is loaded by iBoot from the installed macOS; Linux talks to whatever version is there. The driver's
  InitData layout is keyed by firmware version.
- The public 27.2 and the 27.3 beta 1 firmware share the InitData layout except one hardware-data word, so one port
  covers both ("27.2+"). The 27.0 layout differs.
- On the J716s (G17S, firmware 27.3 26C5035r) the port is accepted on the first try:
  `M5 primary initdata acknowledged`, `M5 secondary initdata acknowledged`, `[drm] Initialized aurora 1.0.0`.

## Userspace

- **Vulkan:** Aurora's Vulkan driver runs compute and render work on the G17S (`Apple M5 Pro (G17S B1)`).
- **OpenGL:** the M5 kernel requires each render submission to carry its program list (render resources). Native Gallium
  did not send it at first, so GL ran through zink on Vulkan; the native Gallium path for G17S and G17C now sends it and
  runs the J716s desktop (aurora-silicon/mesa #194). glmark2 inside Hyprland: about 1278 native against 597-890 on zink.
- Scanout on the J716s daily is still simpledrm (a CPU copy) until the DCP driver is in the daily
  (see [display-dcp](../display-dcp/README.md)).

## Per-board data

- **Voltage tables differ per board.** TripleU613 reports that the J714s GPU performance states differ from the J716s
  table in #1173 in 13 of 14 states, several J716s values sitting below the J714s bins; a J716s table must not be used on
  a J714s. Treat these tables as per board (or per unit) until two units of the same board show the same values.
- **J714c (G17C):** the firmware runs, but the scheduler does not pick up jobs yet (edimoldovan's report); earlier the
  `cs` power domain and the PMP were the suspects.

## Results and PRs

- J716s: [firmware boot, Vulkan, zink, Hyprland on the GPU, daily promotion](../../machines/j716s/results/2026-11-07-gpu-e2b-zink.md),
  [native Gallium as the desktop's GL](../../machines/j716s/results/2026-11-08-gl-native.md).
- PRs: aurora-silicon/linux #1012 (M5 GPU base), #1173 (InitData for 27.2 and 27.3); aurora-silicon/mesa #194;
  omacom/m1n1 #37 (GPU hand-off).
