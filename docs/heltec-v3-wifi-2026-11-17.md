# Heltec V3 Wi-Fi radio control

The two Heltec V3 receive radios now use authenticated Wi-Fi/TCP modem control
instead of Pi USB serial. They remain separate physical receivers in the same
logical per-frequency RF fabric. Radio roles, routing, observer deduplication,
frequencies, modem parameters, and CAD settings are unchanged.

- SMF receiver: 909.875 MHz, BW 62.5 kHz, SF9, CR5.
- SFO receiver: 910.525 MHz, BW 62.5 kHz, SF7, CR5.
- Both use the existing official `v1.4.0-heltec` modem firmware and OpenHop's
  existing `modem_tcp` driver, with distinct authentication tokens.
- The RAK remains on USB. The two Station G3 transports are unchanged.

Wi-Fi credentials and modem hostnames persist in radio NVS. OpenHop's persistent
configuration selects TCP, restores RF configuration after radio reconnect, and
its existing systemd service remains enabled at boot. The gateway allows only
the Pi to initiate TCP port 5055 to these radios, with established return traffic.
No public port or general inter-VLAN allowance was added.

## Verification

Both radios passed authenticated TCP firmware-version and RF-configuration
readback. Natural received packets were observed over TCP from both radios;
no RF test transmissions were generated. Production OpenHop established direct
TCP sessions to both radios. Each radio was reset individually: Wi-Fi settings
survived, OpenHop automatically reconnected, and the receiver configuration was
restored. Connection loss detection is not instantaneous; in this test recovery
occurred after the existing driver noticed the broken sockets.

Only deployment configuration changed; no firmware or Core driver patch was
required. Production secrets and private configuration are not included here.

## Provisioning note

On CP2102-based Heltec boards, `dsrdtr=True` means pyserial skips applying the
pre-open DTR state. Explicitly deassert DTR after opening the serial port before
issuing a software reboot/provisioning command. A held PRG/GPIO0 at firmware boot
can invoke the five-second Wi-Fi factory-reset behavior. This caused accepted
provisioning settings to disappear during initial verification; explicit line
release resolved it.

## Power after migration

The V3s still require power. Move each USB cable from the Pi to a suitable USB
power supply (one radio at a time) to free the data ports. Keep the LoRa antennas
connected. USB data is no longer required for normal OpenHop operation; radio
firmware recovery may still require a physical USB connection.
