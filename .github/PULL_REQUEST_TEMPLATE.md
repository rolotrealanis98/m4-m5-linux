## What this changes

<!-- One board, one topic, or the tooling. Say which. -->

Board(s) touched: <!-- e.g. J716s, or "none" -->

## Checklist

- [ ] Each changed state has an evidence link; every `works-*` state links a result file from that board with `kind: native`.
- [ ] Results come from a run on the named machine (not from a tool's summary of what should have happened).
- [ ] Logs are scrubbed: no serial numbers, ECID, nonces, MAC or Bluetooth addresses, IP addresses, host names, user
      names, home paths, Wi-Fi names or passphrases, partition UUIDs.
- [ ] No binaries, firmware, boot objects, ADT/device-tree dumps or NVRAM dumps; build recipes carry hashes only.
- [ ] Claims from other people are entered as `kind: reported` with a link; nothing is copied from unlicensed repositories.
- [ ] Mirrored patches (if any) carry their licence and a `PROVENANCE.yaml` with an upstream PR or target.
- [ ] `python3 tools/validate.py`, `python3 tools/privacy_scan.py`, `python3 tools/gen.py --check` and
      `python3 -m pytest -q tests` pass locally.
- [ ] I offer this text under the licence of the paths it touches (CC-BY-SA-4.0 for docs and data, MIT for tools).

AI assistance (optional): <!-- a sentence is welcome, no trailer required -->
