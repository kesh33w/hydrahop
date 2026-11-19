"""Enrollment routes devices through the node's configured home radio."""
import pytest

from host_enrollment import stage_routes


def config(radios, default=None):
    c = {'radios': [{'id': r} for r in radios],
         'private_island': {'enabled': True, 'node_id': 'host', 'transport': {'peer_fingerprints': {}}}}
    if default:
        c['fabric'] = {'default_radio': default}
    return c


def test_routes_use_the_fabric_default_radio():
    out = stage_routes(config(['g3909', 'g3910'], 'g3909'), 'device-a', 'fp-a')['private_island']
    assert out['inbound'] == [{'peer': 'device-a', 'radio': 'remote-rf', 'local_radio': 'g3909'}]
    assert out['outbound'] == {'g3909': ['device-a']}
    assert out['transport']['peer_fingerprints'] == {'device-a': 'fp-a'}


def test_without_a_fabric_the_legacy_host_rf_name_still_works():
    out = stage_routes(config(['host-rf']), 'device-a', 'fp-a')['private_island']
    assert out['outbound'] == {'host-rf': ['device-a']}


def test_missing_home_radio_is_rejected():
    with pytest.raises(ValueError, match="'g3909' is missing"):
        stage_routes(config(['g3910'], 'g3909'), 'device-a', 'fp-a')


def test_existing_route_on_another_radio_conflicts():
    c = config(['g3909', 'g3910'], 'g3909')
    c['private_island']['outbound'] = {'g3910': ['device-a']}
    with pytest.raises(ValueError, match='outbound route conflicts'):
        stage_routes(c, 'device-a', 'fp-a')
