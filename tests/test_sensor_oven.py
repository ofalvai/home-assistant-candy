"""Tests for various sensors"""
from pytest_homeassistant_custom_component.common import MockConfigEntry, load_fixture
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry, device_registry

from .common import init_integration


async def test_main_sensor_idle(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker):
    await init_integration(hass, aioclient_mock, load_fixture("oven/idle.json"))

    state = hass.states.get("sensor.oven")

    assert state
    assert state.state == "Idle"
    assert state.attributes == {
        "program": 2,
        "selection": 1,
        "temperature": 154,
        "temperature_reached": False,
        "program_length_minutes": 0,
        "remote_control": False,
        "friendly_name": "Oven",
        "icon": "mdi:stove"
    }


async def test_main_sensor_heating(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker):
    await init_integration(hass, aioclient_mock, load_fixture("oven/heating.json"))

    state = hass.states.get("sensor.oven")

    assert state
    assert state.state == "Heating"
    assert state.attributes == {
        "program": 3,
        "selection": 2,
        "temperature": 143,
        "temperature_reached": True,
        "program_length_minutes": 0,
        "remote_control": False,
        "friendly_name": "Oven",
        "icon": "mdi:stove"
    }


async def test_temp_sensor_heating(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker):
    await init_integration(hass, aioclient_mock, load_fixture("oven/heating.json"))

    state = hass.states.get("sensor.oven_temperature")

    assert state
    assert state.state == "143"
    assert state.attributes == {
        "friendly_name": "Oven temperature",
        "icon": "mdi:thermometer",
        "unit_of_measurement": '°C'
    }


async def test_main_sensor_device_info(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker):
    await init_integration(hass, aioclient_mock, load_fixture("oven/idle.json"))

    er = entity_registry.async_get(hass)
    dr = device_registry.async_get(hass)
    entry = er.async_get("sensor.oven")
    device = dr.async_get(entry.device_id)

    assert device
    assert device.manufacturer == "Candy"
    assert device.name == "Oven"
    assert device.suggested_area == "Kitchen"


async def test_sensors_device_info(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker):
    await init_integration(hass, aioclient_mock, load_fixture("oven/idle.json"))

    er = entity_registry.async_get(hass)
    dr = device_registry.async_get(hass)

    main_sensor = er.async_get("sensor.oven")
    temp_sensor = er.async_get("sensor.oven_temperature")

    main_device = dr.async_get(main_sensor.device_id)
    temp_device = dr.async_get(temp_sensor.device_id)

    assert main_device
    assert temp_device
    assert main_device == temp_device
