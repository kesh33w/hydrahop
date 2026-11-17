# CAD on/off, November 17, 2026

Each supported USB/TCP modem has a CAD-before-transmit setting on the CAD page.
Off skips host channel-activity checks only after the modem acknowledges its own
auto-CAD gate is disabled. On uses the host CAD loop. The default/unset state
preserves existing behavior. Explicit modes persist per physical radio and are
restored on reconnect. Unsupported firmware returns an error, not a false success.

Core: `20f0e237fe707e32517aae95c2de7721679e36ce`.
Repeater: `681b134006fd94fa0e4202740f821ea8d0f688d0`.
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
