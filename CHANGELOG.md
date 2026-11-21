# Changelog

Changes to this hub: the Internet Link sidecar, enrollment, component pins and docs. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Coordinated releases are HydraHop versions (`MAJOR.MINOR.PATCH`), tagged `hydrahop-vX.Y.Z` across the core, repeater, web UI and hub repositories. Releases up to 19 Nov 2026 used date tags (`kesh-YYYY.MM.DD`). Firmware releases keep their own tags.

## [Unreleased]

## [1.5.1] - 2026-11-21

### Changed

- **HydraHop marker is a fork icon** (web UI). Menu items and the Dashboard card heading used the letters "HH", which are a hate symbol; they now show a small fork icon with the tooltip "HydraHop feature".
- **Pins** move to `hydrahop-v1.5.1`. Core is unchanged from 1.4.0 (same commit, tagged again).

## [1.5.0] - 2026-11-21

### Added

- **HydraHop status on the Dashboard** (web UI). One card shows, per network, bridged and repeated packets, each antenna's identity codes, which antenna's copy neighbours relay more when sent first, and Internet Link peers.
- **Retired one-byte codes are shown** (web UI and repeater). The Dashboard, Analytics → Antennas and Crossing diagnostics name the radio, the code and the relay that caused it; the API gives `retired_reasons`.
- **HydraHop features are marked in the menu** (web UI): a small HydraHop marker on Bridge, Antennas, Bridge settings and Radio Names, and a dot on pages changed in this release until opened.

### Changed

- **Pins** move to `hydrahop-v1.5.0`. Core is unchanged from 1.4.0 (same commit, tagged again).

## [1.4.2] - 2026-11-21

### Fixed

- **One-byte codes were retired by relays far away** (repeater). Adverts reach the Pi from across the state, and 1.4.1 retired three of its four codes at startup over repeaters 5 to 9 hops away. Only a repeater or room heard within 2 hops now retires a code.

### Changed

- **Pins** move to `hydrahop-v1.4.2`. Core and web UI are unchanged from 1.4.0 (same commits, tagged again).

## [1.4.1] - 2026-11-21

### Added

- **One-byte antenna identity codes** (repeater). `tx_identity_experiment.one_byte`, e.g. `{g3909: [d4, "14"], rak909: ["12", d3]}`, gives a transmitter a hand-picked 1-byte code (plus one for bridged hops), so 1-byte floods are tagged and **Analytics → Antennas** / `GET /api/relay_stats` can tell the copies apart. Pick bytes no relay on that radio's mesh uses. A code is retired as soon as a repeater or room advertising that byte is heard, live or in the last 30 days of stored adverts.

### Fixed

- **Relay stats could credit the wrong copy** (repeater) when an older hop in the path shared a code's bytes.

### Changed

- **Pins** move to `hydrahop-v1.4.1`. Core and web UI are unchanged from 1.4.0 (same commits, tagged again).

## [1.4.0] - 2026-11-20

### Added

- **Which copy did neighbours relay?** (repeater and web UI). For packets a TX group sends through two radios, **Analytics → Antennas** and `GET /api/relay_stats` show how often neighbours relayed each radio's copy, split by whether it went first or second, and which neighbours relayed which copy. It reads the identity code each copy carried from the relays this node hears back, so it needs per-radio identity codes (`tx_identity_experiment` with `mode: tx`); copies on 1-byte paths or direct routes cannot be told apart and are counted separately.
- **Random double-TX order** (core and repeater). `fabric.topology.tx_group_orders: {g3909: random}` shuffles which radio sends first for every send, so neither radio wins relays just by going first. Default `fixed`.

### Changed

- **Pins** move to `hydrahop-v1.4.0`.

## [1.3.3] - 2026-11-20

### Added

- **Pause between double-TX sends** (core and repeater). `fabric.topology.tx_group_gaps_ms`, e.g. `{g3909: [300, 1200]}`, waits a random time in that range (ms) before a TX group's second radio sends, instead of keying up the instant the first finishes, when neighbours are rebroadcasting the first copy. Off unless set; config file only.

### Fixed

- **Shadow radios could be configured as TX-group transmitters** (core and repeater). Shadow radios are receive-only: a TX group naming one is now refused at startup and at send time, and the web UI no longer offers one. `receiver` radios can still be the second transmitter.

### Changed

- **Pins** move to `hydrahop-v1.3.3`. The web UI is unchanged from 1.3.1 (same commit, tagged again).

## [1.3.2] - 2026-11-20

### Fixed

- **Double-TX radios showed zero transmit airtime** (repeater). Each leg of a TX group is now recorded against its own radio in `tx_radio_ids`, so the dashboard airtime chart, per-radio packet rates and MQTT `tx_radio_ids` count the group's second radio (e.g. `rak909`, `rak910`). Rows stored before the upgrade keep the old attribution.

### Changed

- **Pins** move to `hydrahop-v1.3.2`. Core and web UI are unchanged from 1.3.1 (same commits, tagged again).

## [1.3.1] - 2026-11-20

### Fixed

- **Antenna and bridge statistics** (repeater and web UI), after an independent review:
  - the antenna signal comparison uses the same radio frame only (same packet, same relay, within 1 s), leads with SNR and states how many frames it rests on; coverage still counts distinct packets;
  - neighbours repeating packets this node bridged are left out of coverage and signal, and counted separately;
  - each antenna shows whether the running topology sends on it, and "no data" / "not recorded" are no longer shown as zero;
  - bridge antenna codes come from the bytes actually sent, not today's settings;
  - a failed history read is reported as an error, not as an empty report.
- **Reproducible installs:** the repeater pins core to an exact commit (including its `hardware` extra) instead of following core's branch.

### Changed

- **Pins** move to `hydrahop-v1.3.1`.

## [1.3.0] - 2026-11-20

### Added

- **Antenna comparison** (repeater and web UI): a new **Analytics → Antennas** page shows, for each network, which antennas heard each packet and how many only one antenna caught, the signal difference between antennas, and per antenna the noise floor, corrupted packets, repeaters heard, sends and channel-busy waits. It reads stored history (`GET /api/antenna_stats`).

### Changed

- **Pins** move to `hydrahop-v1.3.0`.

## [1.2.0] - 2026-11-20

### Added

- **Bridge statistics** (repeater and web UI): a new **Analytics → Bridge** page shows packets bridged each way between the two networks, local repeats, why heard packets were not sent, and sends per antenna pair with each pair's antenna code, over 1 h to 7 days. It reads the repeater's stored packet history (`GET /api/bridge_stats`), so it needs no new tracking and survives restarts.

### Changed

- **Pins** move to `hydrahop-v1.2.0`.

## [1.1.0] - 2026-11-19

### Added

- **Antenna alias names on maps** (repeater): every MQTT status message lists the antenna aliases with labels such as `BD6E g3910→rak910`. The SacMesh CoreScope fork names alias hops from it, for observers it trusts (`hopAliases` setting).

### Changed

- **Pins** move to `hydrahop-v1.1.0`.

## [1.0.3] - 2026-11-19

### Fixed

- **G3 receptions carry RSSI/SNR** (core): the TCP modem driver now passes each packet's own signal metrics. Before this, about a quarter of the MQTT observations on CoreScope had no RSSI or SNR.

### Changed

- **Pins** move to `hydrahop-v1.0.3`.

## [1.0.2] - 2026-11-19

### Fixed

- **MQTT observers report relayed copies** (repeater): each relay path of a packet is now its own observation, as with single-radio observer firmware. Before this, CoreScope showed about a third as many observations as a co-located Heltec observer.

### Changed

- **Pins** move to `hydrahop-v1.0.2`.
- **Docs:** examples and diagrams use the radio IDs `g3909` and `g3910` (formerly `host-rf` and `bay`), matching `rak909` and `rak910`.

## [1.0.1] - 2026-11-19

### Fixed

- **iLink enrollment** routes a new device through the configured home radio (`fabric.default_radio`) instead of a radio that had to be named `host-rf`. Renaming radios no longer breaks enrollment.

### Changed

- **Pins** move to `hydrahop-v1.0.1`.

## [1.0.0] - 2026-11-19

The first release under the HydraHop name.

### Changed

- **The hub is renamed** from `kesh-openhop-bridge` to `hydrahop`. GitHub redirects the old address; links now use the new one.
- **Versioning**: releases are now HydraHop semantic versions tagged `hydrahop-vX.Y.Z` across all four repositories. Date tags (`kesh-YYYY.MM.DD`) stay as history.
- **Pins** move to `hydrahop-v1.0.0`: the observer label reads `💧🍴 OpenHop HydraHop v1.0.0`, and the Victron sensor no longer drops data waiting during a slow port open.
- **The upgrade guide** targets `hydrahop-v1.0.0`.
- **The project is named HydraHop**, an OpenHop fork. README title and NOTICE follow.

## [kesh-2026.11.19] - 2026-11-19

### Changed

- **Pins** move to `kesh-2026.11.19`. No radio behaviour changes: this release fixes the reported version and the upgrade guide, and readies the repositories for outside readers.
- **The upgrade guide** targets `kesh-2026.11.19`.
- **README** opens with a "Start here" overview of the four repositories, and makes this repository's issues the single place for feedback on all of them.
- **The upgrade guide** now switches the plugin manager's drop-in along with the repeater's, and backs up, verifies and rolls back both. Before this, upgrades left the plugin manager on an old release.
- **The upgrade guide** records the 19 Nov 2026 Pi cleanup, replaces the one-off removal list with a general check before deleting a release, and explains why `/opt/openhop_repeater/` stays (waterfall-metadata uses its venv).
- The Antenna identities row points at the web UI setting.

### Fixed

- **Reported version.** `enrollment/pi_enrollment_entry.py` overwrote the repeater and core versions with hardcoded `61e5ffa.ilinkui20261105` strings, so every release since 5 Nov 2026 reported itself as that build in the web UI, the update check and observer MQTT `software_version`. The override is removed; the installed package versions are reported.
- A duplicate `### Changed` heading under `kesh-2026.11.18.1`.

## [kesh-2026.11.18.2] - 2026-11-19

### Changed

- **Pins** move to `kesh-2026.11.18.2`, which adds an Antenna identities setting (Bridge settings → Transmitters) to switch between a single identity and antenna codes.
- **The upgrade guide** targets `kesh-2026.11.18.2`.

## [kesh-2026.11.18.1] - 2026-11-18

### Changed

- **Pins** move to `kesh-2026.11.18.1`. Its bundled web UI includes the Bridge control center and the Radio names editor, which the Pi has served unmerged since 2026-11-17. Upgrading to `kesh-2026.11.18` would have removed them.
- **The upgrade guide** targets `kesh-2026.11.18.1` and explains why `web.web_path` is safe to repoint.
- The upgrade guide lists `/opt/openhop-channel-bridge/` for removal, and the README names the archived predecessor repositories.

## [kesh-2026.11.18] - 2026-11-18

### Added

- [Upgrade guide](docs/upgrade.md) for installing a tagged release as a new release directory on the Pi, with verification and rollback.
- `components.current.json` pinned to the `kesh-2026.11.18` tags of core, repeater and web UI.
- CHANGELOG, SECURITY, PR template, and CI that runs the sidecar and integration tests against core and repeater `kesh/bridge`.

### Fixed

- **Enrollment** read-modify-wrote `config.yaml` without openHop's config lock, so a web UI settings save at the same moment could drop the newly enrolled peer or the operator's change.
  - Enrollment now writes under `_CONFIG_WRITE_LOCK`, in a worker thread, so the radio loop never waits on the fsync.
  - The rewritten file keeps its owner and mode.

[Unreleased]: https://github.com/kesh33w/kesh-openhop-bridge/compare/kesh-2026.11.18.2...kesh/openhop-bridge
[kesh-2026.11.18.2]: https://github.com/kesh33w/kesh-openhop-bridge/compare/kesh-2026.11.18.1...kesh-2026.11.18.2
[kesh-2026.11.18.1]: https://github.com/kesh33w/kesh-openhop-bridge/compare/kesh-2026.11.18...kesh-2026.11.18.1
[kesh-2026.11.18]: https://github.com/kesh33w/kesh-openhop-bridge/releases/tag/kesh-2026.11.18
