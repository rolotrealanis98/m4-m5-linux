# Power: idle, frequency, sleep and the SMC on the T6050

## CPU idle

- With `idle=nop` every core spins: about 16 W at idle on the J716s and 15 W on the J714s.
- WFI loses general-purpose and FP/SIMD state on the non-boot cores unless the kernel preserves registers across it.
  With Aurora's register-preserving idle path the cores really sleep: J716s 16.4 W to about 9.8 W on the charger,
  J714s 15.3 W to 5.6 W (betizzel). Keep `arm64.nowfxt` and `kvm-arm.wfi_trap_policy=trap`.
- m1n1 still appends `idle=nop`; the J716s kernel ignores it for WFI (aurora-silicon/linux #1152).

## Frequency

- Three clusters, three cpufreq policies. Without OPP tables for clusters 1 and 2 the cores run where the firmware left
  them (J714s P cores measured at 1307 MHz). The ADT's voltage-state tables give the steps; boost states are marked
  turbo-mode on the J716s.
- betizzel measured on the J714s that hardware p-state N runs at ADT table entry N-2; check `scaling_cur_freq` against a
  measured clock on other boards.
- The power-management controller (PMC) and the CLPC can be observed without writing anything (J716s test kernel);
  writing floors is the next, attended step. The PMP coprocessor is reported running on the J714c.

## Sleep

- s2idle works with the lid as a wake source through `macsmc-input`; a lid-open report during sleep is confirmed
  against the SMC before it wakes the machine (aurora-silicon/linux #1160).
- The adopted N1 port must stay up through s2idle (see [n1-wireless](../n1-wireless/README.md)).
- J714s: an unused debug UART faulted on the second suspend in a boot until its power domain was taken around the
  resume (betizzel).

## SMC

- Battery and charger through `macsmc-power`: its work items must be initialised before the power-supply notifier,
  or the probe hangs the machine.
- hwmon: the T6050 fan mode keys are `F0md`/`F1md`; there is no fan-control unlock key.

## Results and PRs

- J716s: [WFI idle and sleep](../../machines/j716s/results/2026-11-07-wfi-idle-and-sleep.md), [lid sleep](../../machines/j716s/results/2026-11-07-lid-sleep-n1.md),
  [battery](../../machines/j716s/results/2026-11-07-r3s-battery.md), [sensors](../../machines/j716s/results/2026-11-07-hwmon-t1.md), [PMC observe](../../machines/j716s/results/2026-11-07-power-t1.md).
- PRs: aurora-silicon/linux #1152, #1160, #1084, #481 (T6050 cpufreq profile, held discussion).
