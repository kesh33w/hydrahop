# Internet Link (iLink)

Kesh uses iLink as a temporary compatibility workaround for an older-firmware repeater. Kesh reports that the regional switch to two-byte paths left people behind that repeater cut off from multibyte traffic.

The current implementation admits only eligible packets with two- or three-byte path hashes on approved iLink routes. One-byte traffic stays on normal RF. In this installation, that means continuing to rely on the existing older repeater for single-byte traffic. Multibyte traffic also retains normal RF forwarding under its own policy. This describes the intended topology, not automatic fallback selection or guaranteed delivery.

The TLS Internet Link connects the Pi to MeshCore Observer-based Heltec V4.3 radios. The TFT build has touchscreen Wi-Fi setup. The standard OLED build uses a phone setup portal and USER-button recovery. Both generate their own identity and enrollment credentials during installation. Local RF startup remains independent of optional link failures.

The TFT iLink firmware and the OpenHop USB bench modem are separate components. The USB bench targets support Heltec T096 and V4.3 hardware with restricted radio profiles and transmit power.

## Peer status

Internet Link peer status includes `last_valid_inbound_frame_age_seconds`, measured with a monotonic clock. It is `null` until a complete inbound frame passes validation. Its captured arrival time is recorded immediately after validation, before replay admission or RF planning can wait or fail. The age is retained across disconnects and reconnects, and resets when the service process restarts. Valid duplicates and frames rejected by downstream admission or RF planning still count as link activity. Neither connection status nor frame activity establishes RF transmission or recipient delivery.

## Firmware and enrollment

For hardware-specific setup and builds, see the [V4.3 TFT guide](https://github.com/kesh33w/MeshCore/blob/kesh/v43-tft-ilink/OPENHOP-BRIDGE-TFT.md) or [V4.3 OLED guide](https://github.com/kesh33w/MeshCore/blob/kesh/v43-oled-ilink/OPENHOP-BRIDGE-OLED.md).

The private link sidecar must be on the daemon's Python path. `enrollment/pi_enrollment_entry.py --check` checks imports without starting a service. Activation requires explicit configuration, CA, issuer-key, and state paths. Configure routes and trust deliberately before activation.
