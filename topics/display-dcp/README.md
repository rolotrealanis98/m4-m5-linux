# Display (DCP) on the T6050

## What is known

- The display coprocessor firmware comes from macOS like the GPU's. Its method numbers and swap layouts differ between
  firmware 27.x builds and are not interchangeable: 27.3 beta 1 is 27.2 plus one method and a larger swap request.
  Unknown firmware builds should be refused rather than treated as another version.
- The loader hands over the running DCP and the framebuffer iBoot set up (omacom/m1n1 #35), and the firmware-27 driver
  negotiates with it instead of restarting it.
- The device-tree node needs the internal panel's bandwidth scratch offset (`apple,bw-scratch`) or the driver refuses
  the tree, and the display clock of the `disp0` pipe (not the empty clock list of the `dcp` node) or the firmware
  complains about an undeclared clock provider.
- **Swap timestamps:** counter-based timestamps on 120 Hz swaps stalled the first swap after the mode set; constant
  timestamps fix it.
- **Modes:** the J716s firmware offers six timings at 3456x2234 (120 Hz preferred, 60, 59.94, 50, 48, 47.95). VRR is an
  opt-in and changes the measured flip interval.
- **Formats:** betizzel reports that on the J714s the firmware treats the X byte of XRGB as alpha, so the console and
  compositor must use alpha formats (a Hyprland change was needed).
- **Brightness:** on the J716s writes are accepted but do not reach the panel yet; edimoldovan (J714c) and betizzel
  (J714s) report working brightness control.

## Status by board

- J716s: works on test payloads; the first daily candidate with the DCP and the GPU hand-off together panicked early and
  is being bisected.
- J714c, J714s: the DCP drives the internal panel (reported).

## Results and PRs

- J716s: [stage C](../../machines/j716s/results/2026-11-07-dcp-stage-c.md), [120 Hz and VRR](../../machines/j716s/results/2026-11-08-dcp-120-vrr.md),
  [daily candidate fallback](../../machines/j716s/results/2026-11-08-daily-dcp-fallback.md).
- PRs: aurora-silicon/linux #1174 (27.3 method table and swap layout), #1012; omacom/m1n1 #35.
