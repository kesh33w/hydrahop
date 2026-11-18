"""Enrollment must not race openHop settings saves on config.yaml."""
import asyncio
import copy
import sys
import threading
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "enrollment"))
import enrollment_server


class _Cert:
    def fingerprint(self, _):
        return bytes.fromhex("ab" * 32)


@pytest.fixture
def controller(tmp_path, monkeypatch):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump({
        "repeater": {"mode": "forward"},
        "private_island": {"transport": {"peer_fingerprints": {}}},
    }))
    gate = threading.Event()
    released = threading.Event()
    lock = threading.RLock()
    monkeypatch.setattr(enrollment_server, "_CONFIG_WRITE_LOCK", lock, raising=False)
    monkeypatch.setattr(enrollment_server, "validate_request", lambda request: (None, "peer-1"))

    def enroll(request, current, ca, key, state, **kwargs):
        candidate = copy.deepcopy(current)
        candidate["private_island"]["transport"]["peer_fingerprints"]["peer-1"] = "ab" * 32
        gate.set()
        released.wait(2)  # Hold the window open for a concurrent settings save.
        return {"certificate_pem": "pem"}, candidate, SimpleNamespace(isoformat=lambda: "2027-11-18")

    monkeypatch.setattr(enrollment_server, "enroll", enroll)
    monkeypatch.setattr(enrollment_server, "_configuration", lambda ns: (None, "routes", 4))
    monkeypatch.setattr(enrollment_server.x509, "load_pem_x509_certificate", lambda data: _Cert())
    ctl = enrollment_server.EnrollmentController.__new__(enrollment_server.EnrollmentController)
    ctl.config_path, ctl.state_dir = config_path, tmp_path
    ctl.ca = SimpleNamespace(not_valid_after_utc=SimpleNamespace(isoformat=lambda: "2036-01-01"))
    ctl.key = None
    ctl.lock = asyncio.Lock()
    return ctl, lock, gate, released


def _service(daemon):
    adapter = SimpleNamespace(transports={}, _send_locks={}, config=None,
                              rf_planner=SimpleNamespace(__self__=SimpleNamespace(daemon=daemon)))
    adapter.receiver = lambda *a: None
    return SimpleNamespace(transports={}, _peers_by_pin={}, settings={},
                           receiver=SimpleNamespace(__self__=adapter))


@pytest.mark.asyncio
async def test_concurrent_settings_save_cannot_drop_enrolled_peer(controller):
    ctl, lock, gate, released = controller
    daemon = SimpleNamespace(config=yaml.safe_load(ctl.config_path.read_text()))
    service = _service(daemon)
    loop_thread = threading.get_ident()

    def openhop_save():
        # What ConfigManager.update_and_save does: serialize in-memory config under the lock.
        gate.wait(2)
        with lock:
            daemon.config["repeater"]["mode"] = "monitor"
            ctl.config_path.write_text(yaml.safe_dump(daemon.config))

    saver = threading.Thread(target=openhop_save)
    saver.start()
    accept = asyncio.create_task(ctl.accept({}, service))
    await asyncio.to_thread(gate.wait, 2)
    # The event loop stays free while enrollment holds the config lock.
    await asyncio.sleep(0)
    assert threading.get_ident() == loop_thread
    released.set()
    await asyncio.wait_for(accept, 5)
    await asyncio.to_thread(saver.join, 5)

    saved = yaml.safe_load(ctl.config_path.read_text())
    assert saved["private_island"]["transport"]["peer_fingerprints"] == {"peer-1": "ab" * 32}
    assert saved["repeater"]["mode"] == "monitor"
    assert service.transports["peer-1"] is service.receiver.__self__.transports["peer-1"]
    assert service.receiver.__self__.config == "routes"
