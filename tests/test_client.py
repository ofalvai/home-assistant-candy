import aiohttp
import pytest
from aresponses import ResponsesMockServer

from custom_components.candy.client import CandyClient, detect_encryption, Encryption
from custom_components.candy.client.model import MachineState, WashProgramState, WashingMachineStatus
from .common import *


@pytest.mark.asyncio
async def test_idle(aresponses: ResponsesMockServer):
    """Test parsing the status when turning on the machine and selecting WiFi mode"""
    aresponses.add(
        TEST_IP,
        "/http-read.json",
        response=status_response("washing_machine/idle.json")
    )

    async with aiohttp.ClientSession() as session:
        client = CandyClient(session, device_ip=TEST_IP, encryption_key=TEST_ENCRYPTION_KEY_EMPTY, use_encryption=False)
        status = await client.status()

        assert type(status) is WashingMachineStatus
        assert status.machine_state is MachineState.IDLE
        assert status.program_state is WashProgramState.STOPPED
        assert status.spin_speed == 800
        assert status.temp == 40

    aresponses.assert_plan_strictly_followed()


@pytest.mark.asyncio
async def test_delayed_start_wait(aresponses: ResponsesMockServer):
    """Test parsing the status when machine is waiting for a delayed start wash cycle"""
    aresponses.add(
        TEST_IP,
        "/http-read.json",
        response=status_response("washing_machine/delayed_start_wait.json")
    )

    async with aiohttp.ClientSession() as session:
        client = CandyClient(session, device_ip=TEST_IP, encryption_key=TEST_ENCRYPTION_KEY_EMPTY, use_encryption=False)
        status = await client.status()

        assert type(status) is WashingMachineStatus
        assert status.machine_state is MachineState.DELAYED_START_PROGRAMMED
        assert status.program_state is WashProgramState.STOPPED
        assert status.remaining_minutes == 50


@pytest.mark.asyncio
async def test_no_fillr_property(aresponses: ResponsesMockServer):
    """Test parsing the status when response doesn't contain the FillR property"""
    aresponses.add(
        TEST_IP,
        "/http-read.json",
        response=status_response("washing_machine/no_fillr.json")
    )

    async with aiohttp.ClientSession() as session:
        client = CandyClient(session, device_ip=TEST_IP, encryption_key=TEST_ENCRYPTION_KEY_EMPTY, use_encryption=False)
        status = await client.status()

        assert type(status) is WashingMachineStatus
        assert status.machine_state is MachineState.IDLE
        assert status.fill_percent is None


@pytest.mark.asyncio
async def test_detect_no_encryption(aresponses: ResponsesMockServer):
    aresponses.add(
        TEST_IP,
        path_pattern="/http-read.json?encrypted=0",
        response=status_response("washing_machine/idle.json"),
        match_querystring=True
    )

    async with aiohttp.ClientSession() as session:
        encryption_type, key = await detect_encryption(session, TEST_IP)

        assert encryption_type is Encryption.NO_ENCRYPTION
        assert key is None

    aresponses.assert_plan_strictly_followed()


@pytest.mark.asyncio
async def test_detect_encryption_key(aresponses: ResponsesMockServer):
    aresponses.add(
        TEST_IP,
        path_pattern="/http-read.json?encrypted=0",
        response={"response": "BAD REQUEST"},
        match_querystring=True
    )

    aresponses.add(
        TEST_IP,
        path_pattern="/http-read.json?encrypted=1",
        response=TEST_ENCRYPTED_HEX_RESPONSE,
        match_querystring=True
    )

    async with aiohttp.ClientSession() as session:
        encryption_type, key = await detect_encryption(session, TEST_IP)

        assert encryption_type is Encryption.ENCRYPTION
        assert key == TEST_ENCRYPTION_KEY

    aresponses.assert_plan_strictly_followed()


@pytest.mark.asyncio
async def test_detect_encryption_without_key(aresponses: ResponsesMockServer):
    aresponses.add(
        TEST_IP,
        path_pattern="/http-read.json?encrypted=0",
        response={"response": "BAD REQUEST"},
        match_querystring=True
    )

    aresponses.add(
        TEST_IP,
        path_pattern="/http-read.json?encrypted=1",
        response=TEST_UNENCRYPTED_HEX_RESPONSE,
        match_querystring=True
    )

    async with aiohttp.ClientSession() as session:
        encryption_type, key = await detect_encryption(session, TEST_IP)

        assert encryption_type is Encryption.ENCRYPTION_WITHOUT_KEY
        assert key is None

    aresponses.assert_plan_strictly_followed()
