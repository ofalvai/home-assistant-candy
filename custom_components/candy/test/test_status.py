import aiohttp

import pytest
from aresponses import ResponsesMockServer

from .common import TEST_IP, TEST_ENCRYPTION_KEY, status_response
from candy.client import CandyClient
from candy.client.model import MachineState, ProgramState


@pytest.mark.asyncio
async def test_idle(aresponses: ResponsesMockServer):
    """Test parsing the status when turning on the machine and selecting WiFi mode"""
    aresponses.add(
        TEST_IP,
        "/http-read.json",
        response=status_response("idle.json")
    )

    async with aiohttp.ClientSession() as session:
        client = CandyClient(session, device_ip=TEST_IP, encryption_key=TEST_ENCRYPTION_KEY, use_encryption=False)
        status = await client.status()

        assert status.machine_state is MachineState.IDLE
        assert status.program_state is ProgramState.STOPPED
        assert status.spin_speed == 800
        assert status.temp == 40

    aresponses.assert_plan_strictly_followed()


@pytest.mark.asyncio
async def test_delayed_start_wait(aresponses: ResponsesMockServer):
    """Test parsing the status when machine is waiting for a delayed start wash cycle"""
    aresponses.add(
        TEST_IP,
        "/http-read.json",
        response=status_response("delayed_start_wait.json")
    )

    async with aiohttp.ClientSession() as session:
        client = CandyClient(session, device_ip=TEST_IP, encryption_key=TEST_ENCRYPTION_KEY, use_encryption=False)
        status = await client.status()

        assert status.machine_state is MachineState.DELAYED_START_PROGRAMMED
        assert status.program_state is ProgramState.STOPPED
        assert status.remaining_minutes == 50
