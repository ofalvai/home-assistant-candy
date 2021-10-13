"""Tests for various sensors"""
from pytest_homeassistant_custom_component.common import MockConfigEntry, load_fixture
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry, device_registry

from .common import init_integration


async def test_main_sensor_idle(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker):
    await init_integration(hass, aioclient_mock, load_fixture("dishwasher/idle.json"))

    state = hass.states.get("sensor.dishwasher")

    assert state
    assert state.state == "Idle"
    assert state.attributes == {
        "program": "P1+",
        "remaining_minutes": 0,
        "eco_mode": False,
        "door_open": False,
        "remote_control": True,
        "friendly_name": "Dishwasher",
        "icon": "mdi:glass-wine"
    }


async def test_main_sensor_wash(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker):
    await init_integration(hass, aioclient_mock, load_fixture("dishwasher/wash.json"))

    state = hass.states.get("sensor.dishwasher")

    assert state
    assert state.state == "Wash"
    assert state.attributes == {
        "program": "P2-",
        "remaining_minutes": 68,
        "eco_mode": True,
        "door_open": False,
        "remote_control": False,
        "friendly_name": "Dishwasher",
        "icon": "mdi:glass-wine"
    }


async def test_remaining_time_sensor_idle(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker):
    await init_integration(hass, aioclient_mock, load_fixture("dishwasher/idle.json"))

    state = hass.states.get("sensor.dishwasher_remaining_time")

    assert state
    assert state.state == "0"
    assert state.attributes == {
        "friendly_name": "Dishwasher remaining time",
        "icon": "mdi:progress-clock",
        "unit_of_measurement": "min",
    }


async def test_remaining_time_sensor_wash(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker):
    await init_integration(hass, aioclient_mock, load_fixture("dishwasher/wash.json"))

    state = hass.states.get("sensor.dishwasher_remaining_time")

    assert state
    assert state.state == "68"
    assert state.attributes == {
        "friendly_name": "Dishwasher remaining time",
        "icon": "mdi:progress-clock",
        "unit_of_measurement": "min",
    }


async def test_main_sensor_device_info(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker):
    await init_integration(hass, aioclient_mock, load_fixture("dishwasher/idle.json"))

    er = entity_registry.async_get(hass)
    dr = device_registry.async_get(hass)
    entry = er.async_get("sensor.dishwasher")
    device = dr.async_get(entry.device_id)

    assert device
    assert device.manufacturer == "Candy"
    assert device.name == "Dishwasher"
    assert device.suggested_area == "Kitchen"


async def test_sensors_device_info(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker):
    await init_integration(hass, aioclient_mock, load_fixture("dishwasher/idle.json"))

    er = entity_registry.async_get(hass)
    dr = device_registry.async_get(hass)

    main_sensor = er.async_get("sensor.dishwasher")
    time_sensor = er.async_get("sensor.dishwasher_remaining_time")

    main_device = dr.async_get(main_sensor.device_id)
    time_device = dr.async_get(time_sensor.device_id)

    assert main_device
    assert time_device
    assert main_device == time_device
