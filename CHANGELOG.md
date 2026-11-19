# Changelog

Changes to this hub: the Internet Link sidecar, enrollment, component pins and docs. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Coordinated releases are tagged `kesh-YYYY.MM.DD` across the core, repeater, web UI and hub repositories. Firmware releases keep their own tags.

## [Unreleased]

### Changed

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

[Unreleased]: https://github.com/kesh33w/kesh-openhop-bridge/compare/kesh-2026.11.18...kesh/openhop-bridge
[kesh-2026.11.18]: https://github.com/kesh33w/kesh-openhop-bridge/releases/tag/kesh-2026.11.18
