"""Tests for various sensors"""
from pytest_homeassistant_custom_component.common import MockConfigEntry, load_fixture
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry, device_registry

from .common import init_integration


async def test_main_sensor_idle(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker):
    await init_integration(hass, aioclient_mock, load_fixture("washing_machine/idle.json"))

    state = hass.states.get("sensor.washing_machine")

    assert state
    assert state.state == "Idle"
    assert state.attributes == {
        'program': 1,
        'temperature': 40,
        'spin_speed': 800,
        'remaining_minutes': 0,
        'remote_control': True,
        'fill_percent': 0,
        'friendly_name': 'Washing machine',
        'icon': 'mdi:washing-machine'
    }


async def test_cycle_sensor_idle(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker):
    await init_integration(hass, aioclient_mock, load_fixture("washing_machine/idle.json"))

    state = hass.states.get("sensor.wash_cycle_status")

    assert state
    assert state.state == "Stopped"
    assert state.attributes == {
        "friendly_name": "Wash cycle status",
        "icon": "mdi:washing-machine"
    }


async def test_remaining_time_sensor_wash(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker):
    await init_integration(hass, aioclient_mock, load_fixture("washing_machine/running_wash.json"))

    state = hass.states.get("sensor.wash_cycle_remaining_time")

    assert state
    assert state.state == "8"
    assert state.attributes == {
        "friendly_name": "Wash cycle remaining time",
        "icon": "mdi:progress-clock",
        "unit_of_measurement": "min",
    }


async def test_remaining_time_sensor_idle(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker):
    await init_integration(hass, aioclient_mock, load_fixture("washing_machine/idle.json"))

    state = hass.states.get("sensor.wash_cycle_remaining_time")

    assert state
    assert state.state == "0"
    assert state.attributes == {
        "friendly_name": "Wash cycle remaining time",
        "icon": "mdi:progress-clock",
        "unit_of_measurement": "min",
    }


async def test_main_sensor_no_fillr(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker):
    await init_integration(hass, aioclient_mock, load_fixture("washing_machine/no_fillr.json"))

    state = hass.states.get("sensor.washing_machine")

    assert state
    assert state.state == "Idle"
    assert state.attributes == {
        'program': 4,
        'temperature': 40,
        'spin_speed': 1000,
        'remaining_minutes': 0,
        'remote_control': False,
        'friendly_name': 'Washing machine',
        'icon': 'mdi:washing-machine'
    }


async def test_main_sensor_no_pr(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker):
    await init_integration(hass, aioclient_mock, load_fixture("washing_machine/no_pr.json"))

    state = hass.states.get("sensor.washing_machine")

    assert state
    assert state.state == "Running"
    assert state.attributes == {
        'program': 6,
        'temperature': 40,
        'spin_speed': 1000,
        'remaining_minutes': 46,
        'remote_control': True,
        'fill_percent': 53,
        'friendly_name': 'Washing machine',
        'icon': 'mdi:washing-machine'
    }


async def test_main_sensor_device_info(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker):
    await init_integration(hass, aioclient_mock, load_fixture("washing_machine/idle.json"))

    er = entity_registry.async_get(hass)
    dr = device_registry.async_get(hass)
    entry = er.async_get("sensor.washing_machine")
    device = dr.async_get(entry.device_id)

    assert device
    assert device.manufacturer == "Candy"
    assert device.name == "Washing machine"
    assert device.suggested_area == "Bathroom"


async def test_sensors_device_info(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker):
    await init_integration(hass, aioclient_mock, load_fixture("washing_machine/idle.json"))

    er = entity_registry.async_get(hass)
    dr = device_registry.async_get(hass)

    main_sensor = er.async_get("sensor.washing_machine")
    cycle_sensor = er.async_get("sensor.wash_cycle_status")
    time_sensor = er.async_get("sensor.wash_cycle_remaining_time")

    main_device = dr.async_get(main_sensor.device_id)
    cycle_device = dr.async_get(cycle_sensor.device_id)
    time_device = dr.async_get(time_sensor.device_id)

    assert main_device
    assert cycle_device
    assert time_device
    assert main_device == cycle_device == time_device
