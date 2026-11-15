import asyncio
import copy
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from private_link.daemon import current_peer_guard
from private_link.tests.test_daemon import setup, cleanup, frame, wire, settled
from repeater.web.internet_link import inspect, update


def api_for(daemon):
    daemon.config['private_island']['transport'] = {'enabled': True, 'port': 7443, 'peer_fingerprints': {'remote': 'a'*64}}
    saved = []
    def save(updates, **kwargs):
        saved.append(copy.deepcopy(updates))
        daemon.config.update(copy.deepcopy(updates))
        return {'success': True}
    service = SimpleNamespace(close=AsyncMock(), start=AsyncMock(), _server=SimpleNamespace(is_serving=lambda: not daemon.private_island.paused), transports=daemon.private_island.adapter.transports)
    daemon.private_island.service = service
    return SimpleNamespace(config=daemon.config, daemon_instance=daemon, config_manager=SimpleNamespace(update_and_save=save)), saved, service


@pytest.mark.asyncio
async def test_toggle_keeps_local_rf_and_replay_and_preserves_configuration():
    rig, daemon, transport = await setup()
    api, saved, service = api_for(daemon)
    before = copy.deepcopy(daemon.config)
    binding = daemon.private_island
    replay = binding.adapter.replay_store
    try:
        await binding.adapter.peer_received(frame(wire(marker=60)), transport)
        await settled(daemon)
        result = await update(api, {'enabled': False})
        assert result == {'saved': True, 'live_updated': True, 'restart_required': False, 'enabled': False}
        assert binding.paused and not binding.closed
        assert binding.adapter.replay_store is replay
        assert not (await inspect(api))['running']
        assert not (await inspect(api))['editable']
        assert (await inspect(api))['service_control_available']
        assert daemon.config == {**before, 'private_island': {**before['private_island'], 'enabled': False}}
        calls = len(transport.frames)
        rx = rig.handler.rx_count
        rig.local.rx_callback(wire(marker=61), -82, 3.0)
        await settled(daemon)
        assert rig.handler.rx_count == rx + 1  # Local radio dispatch still runs.
        assert len(transport.frames) == calls
        assert await binding.adapter.peer_received(frame(wire(marker=62)), transport) == 'disabled'
        result = await update(api, {'enabled': True})
        assert result['live_updated'] and not binding.paused
        assert binding.adapter.replay_store is replay
        assert daemon.config == before
        service.close.assert_awaited_once()
        service.start.assert_awaited_once()
        assert len(saved) == 2
    finally:
        await cleanup(daemon)


@pytest.mark.asyncio
async def test_pending_and_delayed_private_work_does_not_resume_after_enable():
    rig, daemon, transport = await setup()
    api, _, _ = api_for(daemon)
    binding = daemon.private_island
    try:
        await daemon.router.stop()
        assert await binding.adapter.peer_received(frame(wire(marker=64)), transport) == 'rf_planner_accepted'
        packet = daemon.router.queue.get_nowait()
        guard = binding.peer_guard(packet)
        assert guard()
        token = current_peer_guard.set(guard)
        try:
            task = await rig.handler.schedule_retransmit(packet, 0.02)
        finally:
            current_peer_guard.reset(token)
        await update(api, {'enabled': False})
        await update(api, {'enabled': True})
        assert not guard()
        assert await task is False
        assert await daemon.router._route_packet_on_radio(packet) is False
        assert binding.peer_pending == 0
    finally:
        await cleanup(daemon)


@pytest.mark.asyncio
async def test_save_failure_leaves_runtime_and_config_unchanged():
    rig, daemon, _ = await setup()
    api, _, service = api_for(daemon)
    api.config_manager.update_and_save = lambda *a, **k: {'success': False}
    try:
        assert await update(api, {'enabled': False}) is False
        assert daemon.config['private_island']['enabled'] is True
        assert not daemon.private_island.paused
        service.close.assert_not_called()
        assert not api._internet_link_control_pending
    finally:
        await cleanup(daemon)


@pytest.mark.asyncio
async def test_start_failure_reports_saved_desired_state_and_allows_retry():
    rig, daemon, _ = await setup()
    api, _, service = api_for(daemon)
    try:
        await update(api, {'enabled': False})
        service.start.side_effect = OSError('secret path should not appear')
        result = await update(api, {'enabled': True})
        assert result['saved'] and not result['live_updated'] and result['service_error']
        assert daemon.config['private_island']['enabled'] is True
        assert daemon.private_island.paused
        assert 'secret' not in str(result)
        service.start.side_effect = None
        assert (await update(api, {'enabled': True}))['live_updated']
        assert not daemon.private_island.paused
    finally:
        await cleanup(daemon)


@pytest.mark.asyncio
async def test_concurrent_control_and_options_rejected_until_completion():
    rig, daemon, _ = await setup()
    api, _, service = api_for(daemon)
    gate = asyncio.Event()
    service.close.side_effect = gate.wait
    try:
        task = asyncio.create_task(update(api, {'enabled': False}))
        await asyncio.sleep(0)
        await asyncio.sleep(0)
        assert (await inspect(api))['control_pending']
        with pytest.raises(ValueError):
            await update(api, {'enabled': True})
        with pytest.raises(ValueError):
            await update(api, {'max_inflight': 3})
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        gate.set()
        await api._internet_link_control_task
        assert not api._internet_link_control_pending
        assert daemon.private_island.paused
    finally:
        gate.set()
        await cleanup(daemon)


@pytest.mark.asyncio
@pytest.mark.parametrize('data', [{'enabled': 'false'}, {'enabled': 0}, {'enabled': False, 'max_inflight': 3}, {'enabled': True, 'transport': {}}])
async def test_reject_invalid_control_without_saving(data):
    rig, daemon, _ = await setup()
    api, saved, _ = api_for(daemon)
    try:
        with pytest.raises(ValueError):
            await update(api, data)
        assert not saved
    finally:
        await cleanup(daemon)


@pytest.mark.asyncio
async def test_disabled_boot_preserves_peer_and_route_visibility_and_can_start():
    rig, daemon, _ = await setup()
    api, _, _ = api_for(daemon)
    binding = daemon.private_island
    await binding.close()
    daemon.private_island = None
    daemon.config['private_island']['enabled'] = False
    try:
        status = await inspect(api)
        assert status['enabled'] is False and status['running'] is False
        assert status['listener_port'] == 7443
        assert status['peers'] == [{'id': 'remote', 'connected': False}]
        assert len(status['routes']) == 2
        with patch('private_link.daemon.install_from_config', AsyncMock(return_value='installed')) as install:
            result = await update(api, {'enabled': True})
            assert result['live_updated']
            install.assert_awaited_once_with(daemon)
            assert daemon.private_island == 'installed'
    finally:
        daemon.private_island = None
        await cleanup(daemon)
