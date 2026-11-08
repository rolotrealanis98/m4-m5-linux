---
date: 2026-11-07T14:20Z
board: J716s
setup: j716s-aurora73
kind: native
build: "audio kernel with the TDM fixes 0001-0004 (J716 link in the J616s TDM frame), speaker device tree with deferred shutdown, speaker ceiling -30 dB"
kernel: 7.3.0-ge5a4712a3f0d
payload: audio-b6-20261107-6478b765
payload_sha256_prefix: 6478b765
firmware: {os: "27.3 beta 1 (26C5035r), mBoot-20457.60.65.0.1", system: "27.3 beta 1 (26C5035r), mBoot-20457.60.65.0.1"}
attended: true
source: https://github.com/rolotrealanis98/m5pro-linux/blob/f8fd6bc71b2688ca70ad7697cd5506fd2ed393da/contrib/validated/integration/RESULTS.md#result-r3-audio-b6-2026-11-07-1420-utc-rolando-listening-the-speakers-play-clean
features: [audio.speakers]
---

## What was booted

Audio payload B6 with `snd_soc_macaudio.speaker_max_db=-30`; `speakersafetyd` running verbose; the speaker route
set by hand (Mux Secondary, Switch on). Tones: 1 kHz, six channels, 2 s each, raw device, no DSP graph. Rolando listened.

## Results

| Level | Amp IRQ delta | Faults | Daemon peak power |
|---|---|---|---|
| -30 dBFS | +18 | 0 | 0.00 W |
| -20 dBFS | +14 | 0 | 0.00 W |
| -12 dBFS | +20 | 0 | 0.00 W |
| -6 dBFS | +21 | 0 | 0.01 W |
| 0 dBFS | +15 | 0 | 0.04 W |
| left only / right only, -12 dBFS, 3 s | +13 / +14 | 0 | 0.00 W |

Heard by Rolando: "I heard the 1 kHz tone, sounded good, no distortion." `speakersafetyd` stayed up, no limiting, no
warnings.

## Desktop path (same boot)

PipeWire and WirePlumber with the J716 sink fragment: `pw-play` of a 4 s 440 Hz -12 dBFS stereo file at sink volume
1.0 ran the speaker PCM at S24_LE 48 kHz 6 ch, `spkr: pwrd reached`, amp IRQ +16, 0 faults.

## Not tested

A listening check with the tuned J716s speaker profile (staged, not active), and a listen on the exact kernel of the
current daily (the next-daily run played a tone with 0 faults but nobody judged the sound).
