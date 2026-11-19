# Upgrading the Pi to a release

This guide installs a tagged release (currently `hydrahop-v1.0.2`) as a **new release directory** and switches the service to it. The previous release stays in place, so rollback is a one-line change.

Never copy files into an installed virtualenv. Every running file must come from a tagged commit.

## What production looks like

| Item | Path |
|---|---|
| Releases | `/opt/openhop-production/releases/<repeater-sha>.<label>/` (each has `venv/`, `private_link/`, `enrollment/` and `deployment-manifest.json`) |
| Active release | Chosen by two systemd drop-ins, one per service (`ExecStart` + `PYTHONPATH`):<br>`/etc/systemd/system/openhop-repeater.service.d/zz-production.conf`<br>`/etc/systemd/system/openhop-plugin-manager.service.d/production-runtime.conf` |
| Served web UI | `web.web_path` in `/etc/openhop_repeater/config.yaml` |
| Config | `/etc/openhop_repeater/config.yaml`, owned `repeater:repeater`, mode `0600` |
| Backups | `/opt/openhop-production/backups/<label>-<UTC>/` |
| Legacy install | `/opt/openhop_repeater/` is the original pre-release-directory install. Keep it: `waterfall-metadata.service` runs `packet_metadata.py` with its venv, and the plugin manager's start check uses its Python. |
| Python | 3.13 (Debian) |

**Check `web.web_path`.** It should point at the active release's bundled UI (step 4). If it points anywhere else, someone has served a UI build outside a release: compare its text with the new release's bundle before switching, so the upgrade doesn't silently remove a feature. This happened on 17 Nov 2026, when an unmerged UI build was served from an old release directory.

Do not use `kesh-2026.11.18`: its UI lacks the Bridge control center and Radio names.

## Release pins

The exact commits for each release are in [`components.current.json`](../components.current.json). Each repository is tagged with the release name:

| Component | Repository | Tag |
|---|---|---|
| Core | `kesh33w/openhop_core` | `hydrahop-v1.0.2` |
| Repeater (includes the built web UI) | `kesh33w/openhop_repeater` | `hydrahop-v1.0.2` |
| Web UI source | `kesh33w/openHop_RepeaterUI` | `hydrahop-v1.0.2` |
| Internet Link sidecar and enrollment | `kesh33w/hydrahop` | `hydrahop-v1.0.2` |

## 1. Prepare (no service impact)

```sh
TAG=hydrahop-v1.0.2
REL=/opt/openhop-production/releases/$TAG
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
BACKUP=/opt/openhop-production/backups/$TAG-$STAMP

sudo mkdir -p "$BACKUP"
sudo cp -a /etc/openhop_repeater/config.yaml "$BACKUP/"
sudo cp -a /etc/systemd/system/openhop-repeater.service.d "$BACKUP/"
sudo cp -a /etc/systemd/system/openhop-plugin-manager.service.d "$BACKUP/"
sudo mkdir "$REL"            # fails if it already exists: never reuse a release directory
```

## 2. Build the release

```sh
sudo python3.13 -m venv "$REL/venv"
# Core first, at the release tag; then the repeater without letting pip re-resolve core.
sudo "$REL/venv/bin/pip" install "openhop_core[hardware] @ git+https://github.com/kesh33w/openhop_core.git@$TAG"
sudo "$REL/venv/bin/pip" install --no-deps "openhop_repeater @ git+https://github.com/kesh33w/openhop_repeater.git@$TAG"
sudo "$REL/venv/bin/pip" install pyyaml cherrypy paho-mqtt cherrypy-cors==1.7.0 psutil pyserial pyjwt ws4py cryptography

# Internet Link sidecar and enrollment entry point from the hub.
TMP=$(mktemp -d)
git clone --depth 1 --branch "$TAG" https://github.com/kesh33w/hydrahop.git "$TMP/hub"
sudo cp -a "$TMP/hub/private_link" "$TMP/hub/enrollment" "$REL/"
sudo cp "$TMP/hub/components.current.json" "$REL/deployment-manifest.json"
rm -rf "$TMP"
```

Check the build before touching the service:

```sh
sudo "$REL/venv/bin/python" -c "import openhop_core.rf_fabric.topology, repeater.tx_identities; print('imports ok')"
sudo PYTHONPATH="$REL:$REL/enrollment" "$REL/venv/bin/python" "$REL/enrollment/pi_enrollment_entry.py" --check
# Validate the live config against the new code without opening radios:
sudo PYTHONPATH="$REL" "$REL/venv/bin/python" -c "
import yaml; from repeater.config import validate_fabric_config
validate_fabric_config(yaml.safe_load(open('/etc/openhop_repeater/config.yaml'))); print('config ok')"
```

## 3. Review new settings (optional)

These are opt-in, so the upgrade changes nothing until you set them:

| Setting | Effect |
|---|---|
| `fabric.topology.tx_group_scopes: {g3910: crossings}` | Only bridged packets use the SFO transmitter pair |
| Antenna identities (`tx_identity_experiment`) | Switch Off, Transmitting antenna or Receiving + transmitting under **Bridge settings → Transmitters → Antenna identities**; it applies on restart. Production runs `rx_tx` since 19 Nov 2026. |
| `fabric.tx_mode` | Topology now defaults to `sticky` when unset. Production sets it explicitly; check it is still what you want. |

Edit `config.yaml` with an editor that keeps the owner and mode, or through the web UI after the upgrade. If a tool replaces the file, restore `repeater:repeater` ownership before restarting. A wrong owner stopped the service for a minute on 18 Nov.

## 4. Switch (about 10 s of downtime)

```sh
sudo tee /etc/systemd/system/openhop-repeater.service.d/zz-production.conf >/dev/null <<EOF
[Service]
WorkingDirectory=/var/lib/openhop_repeater/production
Environment="PYTHONPATH=$REL:$REL/enrollment"
Environment="PYTHONDONTWRITEBYTECODE=1"
ExecStart=
ExecStart=$REL/venv/bin/python $REL/enrollment/pi_enrollment_entry.py --config /etc/openhop_repeater/config.yaml --enrollment-ca-cert /etc/openhop_repeater/private-link/ca-cert.pem --enrollment-ca-key /etc/openhop_repeater/private-link/issuer-key.pem --enrollment-state-dir /var/lib/openhop_repeater/enrollment-requests --log-level INFO
EOF

sudo tee /etc/systemd/system/openhop-plugin-manager.service.d/production-runtime.conf >/dev/null <<EOF
[Service]
WorkingDirectory=/var/lib/openhop_repeater/production
Environment="PYTHONPATH=$REL:$REL/enrollment"
Environment="PYTHONDONTWRITEBYTECODE=1"
ExecStart=
ExecStart=$REL/venv/bin/python -m repeater.plugins --config /etc/openhop_repeater/config.yaml
EOF
```

Switch both drop-ins together. The plugin manager is a separate service: if only the repeater's drop-in changes, it keeps running the old release's code, and breaks when that release directory is deleted. Until 19 Nov 2026 it was still on a 5 Nov release for exactly this reason.

Point `web.web_path` at the UI built into the release. With Python 3.13 the path is:

```
$REL/venv/lib/python3.13/site-packages/repeater/web/html
```

Then:

```sh
sudo systemctl daemon-reload
sudo systemctl restart openhop-repeater openhop-plugin-manager
```

## 5. Verify

```sh
systemctl is-active openhop-repeater openhop-plugin-manager waterfall-metadata
systemctl show openhop-plugin-manager -p ExecStart --value   # must name $REL
journalctl -u openhop-repeater -n 100 --no-pager | grep -E "ERROR|Traceback|TX identity alias|Packet router registered"
```

- The web UI loads, and **Bridge settings → Crossing diagnostics** shows the antenna identity table.
- `GET /api/tx_groups` returns a `scope` for each network.
- Traffic is being repeated on both networks: watch the dashboard for a few minutes.
- Internet Link peers reconnect (Bridge settings → Internet Link), if it is enabled.
- MQTT brokers do not log a line when they connect, and they connect in a staggered order over up to about 4 minutes. To check, count established connections: `sudo ss -tnp state established | grep "pid=$(systemctl show openhop-repeater -p MainPID --value)" | grep -c ":443"`.
- "Plugin-manager bootstrap skipped: packaged service not found" is harmless. The check looks in `/opt/openhop_repeater/venv`, not the release directory, and the plugin-manager service is already installed.

## Roll back

Restore the previous drop-ins and config, then restart:

```sh
sudo cp -a "$BACKUP/openhop-repeater.service.d/zz-production.conf" /etc/systemd/system/openhop-repeater.service.d/
sudo cp -a "$BACKUP/openhop-plugin-manager.service.d/production-runtime.conf" /etc/systemd/system/openhop-plugin-manager.service.d/
sudo cp -a "$BACKUP/config.yaml" /etc/openhop_repeater/config.yaml
sudo systemctl daemon-reload && sudo systemctl restart openhop-repeater openhop-plugin-manager
```

Restoring `config.yaml` also puts `web.web_path` back on the previous release's UI.

The new release directory can stay for diagnosis. Durable state (the echo ledger and enrollment records) is forward-compatible, so don't delete it.

## Housekeeping after a successful upgrade

Keep the active release and the previous one (for rollback). Once the new release has run well for a while, older release directories can go. Before deleting one, check nothing still uses it:

```sh
OLD=/opt/openhop-production/releases/<old-release>
sudo grep -rl "$OLD" /etc/systemd /etc/openhop_repeater
```

No output means it is safe to remove. Keep `/opt/openhop_repeater/` (see the table above).

**19 Nov 2026 cleanup.** The release directories `08d976a…`, `61e5ffa…` and `99cf1a2…`, the archived prototype's `/opt/openhop-channel-bridge/`, the stale repeater drop-ins (`native-bridge.conf`, `native-private-link.conf`, `zzzz-rak-comparison-20261116.conf`) and the unused `/etc/openhop_repeater/tx-experiment-identities.json` were removed, and the plugin manager was moved to the active release. A copy of everything removed is in the directory named in `/opt/openhop-production/backups/.last-cleanup`.
