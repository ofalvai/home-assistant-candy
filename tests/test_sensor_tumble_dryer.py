"""Tests for various sensors"""
from pytest_homeassistant_custom_component.common import MockConfigEntry, load_fixture
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry, device_registry

from .common import init_integration


async def test_main_sensor_idle(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker):
    await init_integration(hass, aioclient_mock, load_fixture("tumble_dryer/idle.json"))

    state = hass.states.get("sensor.tumble_dryer")

    assert state
    assert state.state == "Idle"

    assert state.attributes == {
        'program': 1,
        'machine_state': 'Idle',
        'program_state': 'Stopped',
        'dry_level_state': 'Ready to Hang',
        'remaining_minutes': 150,
        'remote_control': True,
        'water_tank_full': False,
        'clean_filter': False,
        'friendly_name':
        'Tumble dryer',
        'icon': 'mdi:tumble-dryer'
    }


async def test_main_sensor_device_info(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker):
    await init_integration(hass, aioclient_mock, load_fixture("tumble_dryer/idle.json"))

    er = entity_registry.async_get(hass)
    dr = device_registry.async_get(hass)
    entry = er.async_get("sensor.tumble_dryer")
    device = dr.async_get(entry.device_id)

    assert device
    assert device.manufacturer == "Candy"
    assert device.name == "Tumble dryer"
    assert device.suggested_area == "Bathroom"


async def test_main_sensor_running(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker):
    await init_integration(hass, aioclient_mock, load_fixture("tumble_dryer/running.json"))

    state = hass.states.get("sensor.tumble_dryer")

    assert state
    assert state.state == "Running"

    assert state.attributes == {
        'program': 1,
        'machine_state': 'Running',
        'program_state': 'Drying',
        'dry_level_state': 'Ready to Hang',
        'remaining_minutes': 150,
        'remote_control': True,
        'water_tank_full': False,
        'clean_filter': False,
        'friendly_name': 'Tumble dryer',
        'icon': 'mdi:tumble-dryer'
    }


async def test_main_sensor_hang_level(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker):
    await init_integration(hass, aioclient_mock, load_fixture("tumble_dryer/hang_level.json"))

    state = hass.states.get("sensor.tumble_dryer")

    assert state
    assert state.state == "Running"

    assert state.attributes == {
        'program': 5,
        'machine_state': 'Running',
        'program_state': 'Hang Level Reached',
        'dry_level_state': 'Ready to Iron',
        'remaining_minutes': 122,
        'remote_control': True,
        'water_tank_full': False,
        'clean_filter': False,
        'friendly_name': 'Tumble dryer',
        'icon': 'mdi:tumble-dryer'
    }


async def test_main_sensor_iron_level(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker):
    await init_integration(hass, aioclient_mock, load_fixture("tumble_dryer/iron_level.json"))

    state = hass.states.get("sensor.tumble_dryer")

    assert state
    assert state.state == "Running"

    assert state.attributes == {
        'program': 5,
        'machine_state': 'Running',
        'program_state': 'Iron Level Reached',
        'dry_level_state': 'Ready for closet',
        'remaining_minutes': 122,
        'remote_control': True,
        'water_tank_full': False,
        'clean_filter': False,
        'friendly_name': 'Tumble dryer',
        'icon': 'mdi:tumble-dryer'
    }
