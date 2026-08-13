"""Tests for polling behavior around appliance standby."""

from custom_components.candy.__init__ import _is_idle_or_finished
from custom_components.candy.client.model import (DishwasherState,
                                                  DishwasherStatus,
                                                  MachineState,
                                                  WashingMachineStatus,
                                                  WashProgramState)


def test_dishwasher_finished_is_treated_as_a_terminal_state():
    """Finished dishwashers may turn off their Wi-Fi radio."""
    status = DishwasherStatus(
        machine_state=DishwasherState.FINISHED,
        program="P1",
        remaining_minutes=0,
        delayed_start_hours=None,
        door_open=False,
        door_open_allowed=False,
        eco_mode=False,
        remote_control=False,
        salt_empty=False,
        rinse_aid_empty=False,
    )

    assert _is_idle_or_finished(status)


def test_running_washing_machine_keeps_normal_polling():
    """A connection failure during a cycle must still be surfaced."""
    status = WashingMachineStatus(
        machine_state=MachineState.RUNNING,
        program_state=WashProgramState.WASH,
        program=1,
        program_code=None,
        temp=40,
        spin_speed=800,
        remaining_minutes=60,
        remote_control=True,
        fill_percent=None,
    )

    assert not _is_idle_or_finished(status)
