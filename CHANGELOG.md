# Changelog

Changes to this hub: the Internet Link sidecar, enrollment, component pins and docs. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Coordinated releases are tagged `kesh-YYYY.MM.DD` across the core, repeater, web UI and hub repositories. Firmware releases keep their own tags.

## [Unreleased]

### Changed

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
