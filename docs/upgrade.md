# Upgrading the Pi to a release

This guide installs a tagged release (currently `kesh-2026.11.18.1`) as a **new release directory** and switches the service to it. The previous release stays in place, so rollback is a one-line change.

Never copy files into an installed virtualenv. Every running file must come from a tagged commit.

## What production looks like

| Item | Path |
|---|---|
| Releases | `/opt/openhop-production/releases/<repeater-sha>.<label>/` (each has `venv/`, `private_link/`, `enrollment/` and `deployment-manifest.json`) |
| Active release | Chosen by the systemd drop-in `/etc/systemd/system/openhop-repeater.service.d/zz-production.conf` (`ExecStart` + `PYTHONPATH`) |
| Served web UI | `web.web_path` in `/etc/openhop_repeater/config.yaml` |
| Config | `/etc/openhop_repeater/config.yaml`, owned `repeater:repeater`, mode `0600` |
| Backups | `/opt/openhop-production/backups/<label>-<UTC>/` |
| Python | 3.13 (Debian) |

**Check `web.web_path`.** On 18 Nov 2026 it pointed at `99cf1a2.bridge20261109/ui`, which Codex had overwritten on 17 Nov with an unmerged UI build (the Bridge control center and the Radio names editor). Release `kesh-2026.11.18.1` contains both, plus later features. All but two wordings of the live dashboard's text are present, and those two were reworded on purpose. So step 4, which points `web.web_path` at the release's bundled UI, removes nothing you currently see.

Do not use `kesh-2026.11.18`: its UI lacks the control center and Radio names.

## Release pins

The exact commits for each release are in [`components.current.json`](../components.current.json). Each repository is tagged with the release name:

| Component | Repository | Tag |
|---|---|---|
| Core | `kesh33w/openhop_core` | `kesh-2026.11.18.1` |
| Repeater (includes the built web UI) | `kesh33w/openhop_repeater` | `kesh-2026.11.18.1` |
| Web UI source | `kesh33w/openHop_RepeaterUI` | `kesh-2026.11.18.1` |
| Internet Link sidecar and enrollment | `kesh33w/kesh-openhop-bridge` | `kesh-2026.11.18.1` |

## 1. Prepare (no service impact)

```sh
TAG=kesh-2026.11.18.1
REL=/opt/openhop-production/releases/$TAG
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
BACKUP=/opt/openhop-production/backups/$TAG-$STAMP

sudo mkdir -p "$BACKUP"
sudo cp -a /etc/openhop_repeater/config.yaml "$BACKUP/"
sudo cp -a /etc/systemd/system/openhop-repeater.service.d "$BACKUP/"
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
git clone --depth 1 --branch "$TAG" https://github.com/kesh33w/kesh-openhop-bridge.git "$TMP/hub"
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
| `fabric.topology.tx_group_scopes: {bay: crossings}` | Only bridged packets use the SFO transmitter pair |
| `tx_identity_experiment.mode` | `rx_tx` is the default. It means our hop names both the receiving and the transmitting antenna. Set `tx` to keep the 18 Nov transmit-only behaviour for a first deploy. |
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
```

Point `web.web_path` at the UI built into the release. With Python 3.13 the path is:

```
$REL/venv/lib/python3.13/site-packages/repeater/web/html
```

Then:

```sh
sudo systemctl daemon-reload
sudo systemctl restart openhop-repeater
```

## 5. Verify

```sh
systemctl is-active openhop-repeater
journalctl -u openhop-repeater -n 100 --no-pager | grep -E "ERROR|Traceback|TX identity alias|Packet router registered"
```

- The web UI loads, and **Bridge settings → Crossing diagnostics** shows the antenna identity table.
- `GET /api/tx_groups` returns a `scope` for each network.
- Traffic is being repeated on both networks: watch the dashboard for a few minutes.
- Internet Link peers reconnect (Bridge settings → Internet Link).

## Roll back

Restore the previous drop-in and config, then restart:

```sh
sudo cp -a "$BACKUP/openhop-repeater.service.d/zz-production.conf" /etc/systemd/system/openhop-repeater.service.d/
sudo cp -a "$BACKUP/config.yaml" /etc/openhop_repeater/config.yaml
sudo systemctl daemon-reload && sudo systemctl restart openhop-repeater
```

The new release directory can stay for diagnosis. Durable state (the echo ledger and enrollment records) is forward-compatible, so don't delete it.

## Housekeeping after a successful upgrade

These are safe to remove once the new release is verified:

- `/etc/systemd/system/openhop-repeater.service.d/native-bridge.conf` and `native-private-link.conf`. `zz-production.conf` overrides both.
- `/opt/openhop-channel-bridge/`: releases of the archived channel-bridge prototype. Only the two drop-ins above refer to it, so remove it after them. First confirm nothing else does: `sudo grep -rl openhop-channel-bridge /etc/systemd /etc/openhop_repeater`.
- `zzzz-rak-comparison-20261116.conf`. Its capture window ended on 16 Nov 2026.
- `/etc/openhop_repeater/tx-experiment-identities.json`. These private keys were never used; antenna aliases need only public data.
- Release directories older than the previous one, once you no longer need them for rollback.
