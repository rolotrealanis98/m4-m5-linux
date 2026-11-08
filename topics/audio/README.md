# Audio on the T6050 MacBook Pros

## Pieces

- **Microphones** sit behind the AOP coprocessor (`t8140-aop-audio`): three capsules on the J716s, recorded as a
  three-channel float stream.
- **Speakers:** six TAS2764 amplifiers on the speaker link, a jack codec (CS42L84), and `speakersafetyd` guarding the
  amplifiers; the kernel keeps the volumes locked until the daemon runs.
- The speaker volume ceiling is set in the kernel (`snd_soc_macaudio.speaker_max_db`); the J716s daily uses -30 dB.

## Board differences

- **J716s:** the speaker link only runs clean in the J616s TDM frame; with the J714 serializer settings every amplifier
  logged `bad TDM clock`. edimoldovan reports no such fault on the J714c with the J714 settings, so this is specific to
  the J716s link.
- Apple's J716s speaker tuning is byte-identical to the J616s one, so the J616s DSP graph is the base of a J716s
  profile (built, not yet listened to).
- A udev rule for `speakersafetyd` must match all keys on one parent device, or it never fires and the speakers stay
  silent (the safe failure).

## Results and PRs

- J716s: [microphone](../../machines/j716s/results/2026-11-07-audio-a2-mic.md), [speakers](../../machines/j716s/results/2026-11-07-audio-b6-speakers.md).
- J714c: speakers and microphone reported working ([machines/j714c](../../machines/j714c/machine.yaml)).
- PRs: omacom/omarchy-mac-pkgs #103 (J716s in the audio tests and the manual).
