import pytest

from custom_components.candy.client import CandyClient, detect_encryption, Encryption
from custom_components.candy.client.model import MachineState, WashProgramState, WashingMachineStatus, DishwasherStatus
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


@pytest.mark.asyncio
async def test_status_encryption_with_key(aresponses: ResponsesMockServer):
    aresponses.add(
        TEST_IP,
        "/http-read.json",
        response="2F7C6B441B390C094C3C42093A023429764B1A403343714A6B3D503902342E073D535B6F086854653240386F2E0C23283714243F4B250A0D1A7313085D416B4C5E78686F6A3E191C570D662C1E0B657B76434361344071611A0454390C2026333D120E6F0368484A14443B44644114353503151E4D25084A026B016F416E4D485D53353F5C23163D562613774F53656D597B68441B0F1B071A73137D4F4F4A4B5D78431D4B251F1A592413774F337263787C6B4430683D104C3B50091F1A657B76414361344071611A0641280327282E263E11391B705A581A653C47646A6505311D00346A3E191A4C6B0B6F5D416B4C5E78686F6B2F153C5124546F5741767364534D403343714A7520423E3E022B35764B437C1B66756231401300041034133D1F12281B705A581A653C47646A650E24140F0956250A4A026B016F416E4D485D5333284A2F0C4A026B016F416E4D485D5322255C29133D486B0B6F5D416B4C5E78686F4B7B5A521A7B136160694E487603536F0368484A14443B4464413572764B437F1B6675623140133F59417D6365534D403343714A4A7C13774F53656D597B68441B384E4A026B016F416E4D485D53137A1B705A5B1A653C47646A65336C535B6F086854653240386F1F5A657B763F3401756854653240386F1F5272636E53506F3440711535434C"
    )

    async with aiohttp.ClientSession() as session:
        client = CandyClient(session, device_ip=TEST_IP, encryption_key="TqaM9Jxh8I1MmcGA", use_encryption=True)
        status = await client.status()

        assert type(status) is DishwasherStatus

    aresponses.assert_plan_strictly_followed()


@pytest.mark.asyncio
async def test_status_encryption_without_key(aresponses: ResponsesMockServer):
    aresponses.add(
        TEST_IP,
        "/http-read.json",
        response="7B0D0A20202020227374617475734C6176617472696365223A7B0D0A2020202020202020202020202257694669537461747573223A2230222C0D0A20202020202020202020202022457272223A22323535222C0D0A202020202020202020202020224D6163684D64223A2232222C0D0A202020202020202020202020225072223A223133222C0D0A2020202020202020202020202250725068223A2235222C0D0A20202020202020202020202022534C6576656C223A22323535222C0D0A2020202020202020202020202254656D70223A2230222C0D0A202020202020202020202020225370696E5370223A2230222C0D0A202020202020202020202020224F707431223A2230222C0D0A202020202020202020202020224F707432223A2230222C0D0A202020202020202020202020224F707433223A2230222C0D0A202020202020202020202020224F707434223A2230222C0D0A202020202020202020202020224F707435223A2230222C0D0A202020202020202020202020224F707436223A2230222C0D0A202020202020202020202020224F707437223A2230222C0D0A202020202020202020202020224F707438223A2230222C0D0A20202020202020202020202022537465616D223A2230222C0D0A2020202020202020202020202244727954223A2230222C0D0A2020202020202020202020202244656C56616C223A22323535222C0D0A2020202020202020202020202252656D54696D65223A223130222C0D0A202020202020202020202020225265636970654964223A2230222C0D0A20202020202020202020202022436865636B55705374617465223A2230220D0A202020207D0D0A7D"
    )

    async with aiohttp.ClientSession() as session:
        client = CandyClient(session, device_ip=TEST_IP, encryption_key="", use_encryption=True)
        status = await client.status()

        assert type(status) is WashingMachineStatus

    aresponses.assert_plan_strictly_followed()
