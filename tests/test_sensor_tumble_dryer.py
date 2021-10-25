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
        'remaining_minutes': 150,
        'remote_control': True,
        'dry_level': 2,
        'dry_level_now': 1,
        'refresh': False,
        'need_clean_filter': False,
        'water_tank_full': False,
        'door_closed': True,
        'friendly_name': 'Tumble dryer',
        'icon': 'mdi:tumble-dryer'
    }


async def test_main_sensor_running(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker):
    await init_integration(hass, aioclient_mock, load_fixture("tumble_dryer/running.json"))

    state = hass.states.get("sensor.tumble_dryer")

    assert state
    assert state.state == "Running"
    assert state.attributes == {
        'program': 1,
        'remaining_minutes': 150,
        'remote_control': True,
        'dry_level': 2,
        'dry_level_now': 1,
        'refresh': False,
        'need_clean_filter': False,
        'water_tank_full': False,
        'door_closed': True,
        'friendly_name': 'Tumble dryer',
        'icon': 'mdi:tumble-dryer'
    }


async def test_cycle_sensor_idle(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker):
    await init_integration(hass, aioclient_mock, load_fixture("tumble_dryer/idle.json"))

    state = hass.states.get("sensor.dryer_cycle_status")

    assert state
    assert state.state == "Stopped"
    assert state.attributes == {
        "friendly_name": "Dryer cycle status",
        "icon": "mdi:tumble-dryer"
    }


async def test_cycle_sensor_running(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker):
    await init_integration(hass, aioclient_mock, load_fixture("tumble_dryer/running.json"))

    state = hass.states.get("sensor.dryer_cycle_status")

    assert state
    assert state.state == "Running"
    assert state.attributes == {
        "friendly_name": "Dryer cycle status",
        "icon": "mdi:tumble-dryer"
    }


async def test_remaining_time_sensor_idle(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker):
    await init_integration(hass, aioclient_mock, load_fixture("tumble_dryer/idle.json"))

    state = hass.states.get("sensor.dryer_cycle_remaining_time")

    assert state
    assert state.state == "0"
    assert state.attributes == {
        "friendly_name": "Dryer cycle remaining time",
        "icon": "mdi:progress-clock",
        "unit_of_measurement": "min",
    }


async def test_remaining_time_sensor_running(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker):
    await init_integration(hass, aioclient_mock, load_fixture("tumble_dryer/running.json"))

    state = hass.states.get("sensor.dryer_cycle_remaining_time")

    assert state
    assert state.state == "150"
    assert state.attributes == {
        "friendly_name": "Dryer cycle remaining time",
        "icon": "mdi:progress-clock",
        "unit_of_measurement": "min",
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


async def test_sensors_device_info(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker):
    await init_integration(hass, aioclient_mock, load_fixture("tumble_dryer/idle.json"))

    er = entity_registry.async_get(hass)
    dr = device_registry.async_get(hass)

    main_sensor = er.async_get("sensor.tumble_dryer")
    cycle_sensor = er.async_get("sensor.dryer_cycle_status")
    time_sensor = er.async_get("sensor.dryer_cycle_remaining_time")

    main_device = dr.async_get(main_sensor.device_id)
    cycle_device = dr.async_get(cycle_sensor.device_id)
    time_device = dr.async_get(time_sensor.device_id)

    assert main_device
    assert cycle_device
    assert time_device
    assert main_device == cycle_device == time_device
