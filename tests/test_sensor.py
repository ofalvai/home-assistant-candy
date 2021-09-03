"""Tests for various sensors"""
from pytest_homeassistant_custom_component.common import MockConfigEntry, load_fixture
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker
from homeassistant.const import CONF_IP_ADDRESS, CONF_PASSWORD
from homeassistant.core import HomeAssistant

from custom_components.candy import DOMAIN, CONF_KEY_USE_ENCRYPTION
from tests.common import TEST_IP


async def init_integration(hass: HomeAssistant, aioclient_mock, status_response: str):
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="123-456",
        data={
            CONF_IP_ADDRESS: "192.168.0.66",
            CONF_KEY_USE_ENCRYPTION: False,
            CONF_PASSWORD: "asdasdasd",
        }
    )

    aioclient_mock.get(f"http://{TEST_IP}/http-read.json?encrypted=0", text=status_response)

    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()


async def test_main_sensor_idle(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker):
    await init_integration(hass, aioclient_mock, load_fixture("idle.json"))

    state = hass.states.get("sensor.washing_machine")

    assert state
    assert state.state == "Idle"
    assert state.attributes == {
        'program': 1,
        'temperature': 40,
        'spin_speed': 800,
        'remaining_minutes': 39,
        'remote_control': True,
        'fill_percent': 0,
        'friendly_name': 'Washing machine',
        'icon': 'mdi:washing-machine'
    }


async def test_cycle_sensor_idle(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker):
    await init_integration(hass, aioclient_mock, load_fixture("idle.json"))

    state = hass.states.get("sensor.wash_cycle_status")

    assert state
    assert state.state == "Stopped"
    assert state.attributes == {
        "friendly_name": "Wash cycle status",
        "icon": "mdi:washing-machine"
    }


async def test_remaining_time_sensor_wash(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker):
    await init_integration(hass, aioclient_mock, load_fixture("running_wash.json"))

    state = hass.states.get("sensor.wash_cycle_remaining_time")

    assert state
    assert state.state == "8"
    assert state.attributes == {
        "friendly_name": "Wash cycle remaining time",
        "icon": "mdi:progress-clock",
        "unit_of_measurement": "min",
    }


async def test_main_sensor_no_fillr(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker):
    await init_integration(hass, aioclient_mock, load_fixture("no_fillr.json"))

    state = hass.states.get("sensor.washing_machine")

    assert state
    assert state.state == "Idle"
    assert state.attributes == {
        'program': 4,
        'temperature': 40,
        'spin_speed': 1000,
        'remaining_minutes': 1,
        'remote_control': False,
        'friendly_name': 'Washing machine',
        'icon': 'mdi:washing-machine'
    }
