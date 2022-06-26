import pytest

from custom_components.candy.client import CandyClient, detect_encryption, Encryption
from custom_components.candy.client.model import MachineState, WashProgramState, WashingMachineStatus
from .common import *

from homeassistant.helpers.aiohttp_client import async_get_clientsession


@pytest.mark.asyncio
async def test_idle(hass, aioclient_mock):
    """Test parsing the status when turning on the machine and selecting WiFi mode"""

    aioclient_mock.get(
        f"http://{TEST_IP}/http-read.json",
        text=load_fixture("washing_machine/idle.json")
    )

    client = CandyClient(
        async_get_clientsession(hass), device_ip=TEST_IP, encryption_key=TEST_ENCRYPTION_KEY_EMPTY, use_encryption=False
    )
    status = await client.status()

    assert type(status) is WashingMachineStatus
    assert status.machine_state is MachineState.IDLE
    assert status.program_state is WashProgramState.STOPPED
    assert status.spin_speed == 800
    assert status.temp == 40


@pytest.mark.asyncio
async def test_delayed_start_wait(hass, aioclient_mock):
    """Test parsing the status when machine is waiting for a delayed start wash cycle"""
    aioclient_mock.get(
        f"http://{TEST_IP}/http-read.json",
        text=load_fixture("washing_machine/delayed_start_wait.json")
    )

    client = CandyClient(
        async_get_clientsession(hass), device_ip=TEST_IP, encryption_key=TEST_ENCRYPTION_KEY_EMPTY, use_encryption=False
    )
    status = await client.status()

    assert type(status) is WashingMachineStatus
    assert status.machine_state is MachineState.DELAYED_START_PROGRAMMED
    assert status.program_state is WashProgramState.STOPPED
    assert status.remaining_minutes == 50


@pytest.mark.asyncio
async def test_no_fillr_property(hass, aioclient_mock):
    """Test parsing the status when response doesn't contain the FillR property"""
    aioclient_mock.get(
        f"http://{TEST_IP}/http-read.json",
        text=load_fixture("washing_machine/no_fillr.json")
    )

    client = CandyClient(
        async_get_clientsession(hass), device_ip=TEST_IP, encryption_key=TEST_ENCRYPTION_KEY_EMPTY, use_encryption=False
    )
    status = await client.status()

    assert type(status) is WashingMachineStatus
    assert status.machine_state is MachineState.IDLE
    assert status.fill_percent is None


@pytest.mark.asyncio
async def test_detect_no_encryption(hass, aioclient_mock):
    aioclient_mock.get(
        f"http://{TEST_IP}/http-read.json?encrypted=0",
        text=load_fixture("washing_machine/idle.json")
    )

    encryption_type, key = await detect_encryption(async_get_clientsession(hass), TEST_IP)

    assert encryption_type is Encryption.NO_ENCRYPTION
    assert key is None


@pytest.mark.asyncio
async def test_detect_encryption_key(hass, aioclient_mock):
    aioclient_mock.get(
        f"http://{TEST_IP}/http-read.json?encrypted=0",
        json={"response": "BAD REQUEST"}
    )

    aioclient_mock.get(
        f"http://{TEST_IP}/http-read.json?encrypted=1",
        text=TEST_ENCRYPTED_HEX_RESPONSE
    )

    encryption_type, key = await detect_encryption(async_get_clientsession(hass), TEST_IP)

    assert encryption_type is Encryption.ENCRYPTION
    assert key == TEST_ENCRYPTION_KEY


@pytest.mark.asyncio
async def test_detect_encryption_without_key(hass, aioclient_mock):
    aioclient_mock.get(
        f"http://{TEST_IP}/http-read.json?encrypted=0",
        json={"response": "BAD REQUEST"}
    )

    aioclient_mock.get(
        f"http://{TEST_IP}/http-read.json?encrypted=1",
        text=TEST_UNENCRYPTED_HEX_RESPONSE
    )

    encryption_type, key = await detect_encryption(async_get_clientsession(hass), TEST_IP)

    assert encryption_type is Encryption.ENCRYPTION_WITHOUT_KEY
    assert key is None
