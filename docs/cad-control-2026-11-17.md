# CAD on/off, November 17, 2026

Each supported USB/TCP modem has a CAD-before-transmit setting on the CAD page.
Off skips host channel-activity checks only after the modem acknowledges its own
auto-CAD gate is disabled. On uses the host CAD loop. The default/unset state
preserves existing behavior. Explicit modes persist per physical radio and are
restored on reconnect. Unsupported firmware returns an error, not a false success.

Core: `20f0e237fe707e32517aae95c2de7721679e36ce`.
Repeater: `a94295effe1f78a10ae5cba5ccb89ba5f36de89b`.
UI: `1168d519303e742224f9f09996cb38e86eab2ed9`.

UI production build and mocked browser regression passed, covering no startup
write, selected-radio save, failed acknowledgement display, and unsupported mode.

Validation: 92 core driver/CAD tests and 35 API/calibration tests. Driver transport
mocks verify disabled mode emits no CAD request during send, enabled mode does,
missing firmware acknowledgement preserves host state, and reconnect restores
explicit mode. API tests verify per-radio isolation and preservation across
calibration saves. No RF test transmission or live CAD mode change was made.

Production backend files match published source. The live UI uses an isolated CAD
control asset to retain unrelated existing deployed bundles, and preserves the
CAD page overflow fix. The same control is included in the UI source build.
Historical manifests and firmware pins are unchanged.

## Remote CLI follow-up

The current repeater pin includes `get cad [RADIO_ID]` and
`set cad on|off RADIO_ID` (`1|0` is also accepted). A set on a multi-radio bridge
requires an explicit radio ID. It returns pending while the same serialized
firmware-acknowledgement and persistence path used by the web UI completes;
repeat `get cad` to inspect saved/error status.

The CLI follow-up passed 87 focused CLI/CAD tests and a read-only check of the
running authenticated CLI API. Phone RF transport was not independently tested.
No live CAD mode was changed and no RF test traffic was sent. The repeater commit
is published on `fix/cad-cli`; its default `kesh/bridge` branch remains at the
prior web-control release. This manifest pins the exact deployed CLI commit.
