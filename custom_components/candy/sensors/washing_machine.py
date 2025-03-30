from typing import Any, Mapping

from homeassistant.const import UnitOfTime

from homeassistant.helpers.typing import StateType

from ..const import *
from ..client import WashingMachineStatus
from ..client.model import MachineState
from . import CandyBaseSensor, CandyRemoteControlBaseSensor


class CandyWashingMachineBaseSensor(CandyBaseSensor):

    def device_name(self) -> str:
        return DEVICE_NAME_WASHING_MACHINE

    def suggested_area(self) -> str:
        return SUGGESTED_AREA_BATHROOM


class CandyWashingMachineSensor(CandyWashingMachineBaseSensor):

    @property
    def name(self) -> str:
        return self.device_name()

    @property
    def unique_id(self) -> str:
        return UNIQUE_ID_WASHING_MACHINE.format(self.config_id)

    @property
    def state(self) -> StateType:
        status: WashingMachineStatus = self.coordinator.data
        return str(status.machine_state)

    @property
    def icon(self) -> str:
        return "mdi:washing-machine"

    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        status: WashingMachineStatus = self.coordinator.data

        attributes = {
            "program": status.program,
            "temperature": status.temp,
            "spin_speed": status.spin_speed,
            "remaining_minutes": (
                status.remaining_minutes
                if status.machine_state in [MachineState.RUNNING, MachineState.PAUSED]
                else 0
            ),
            "remote_control": status.remote_control,
        }

        if status.fill_percent is not None:
            attributes["fill_percent"] = status.fill_percent

        if status.program_code is not None:
            attributes["program_code"] = status.program_code

        return attributes


class CandyWashingMachineCycleStatusSensor(CandyWashingMachineBaseSensor):

    @property
    def name(self) -> str:
        return "Wash cycle status"

    @property
    def unique_id(self) -> str:
        return UNIQUE_ID_WASH_CYCLE_STATUS.format(self.config_id)

    @property
    def state(self) -> StateType:
        status: WashingMachineStatus = self.coordinator.data
        return str(status.program_state)

    @property
    def icon(self) -> str:
        return "mdi:washing-machine"


class CandyWashingMachineRemainingTimeSensor(CandyWashingMachineBaseSensor):

    @property
    def name(self) -> str:
        return "Wash cycle remaining time"

    @property
    def unique_id(self) -> str:
        return UNIQUE_ID_WASH_REMAINING_TIME.format(self.config_id)

    @property
    def state(self) -> StateType:
        status: WashingMachineStatus = self.coordinator.data
        if status.machine_state in [MachineState.RUNNING, MachineState.PAUSED]:
            return status.remaining_minutes
        else:
            return 0

    @property
    def unit_of_measurement(self) -> str:
        return UnitOfTime.MINUTES

    @property
    def icon(self) -> str:
        return "mdi:progress-clock"


class CandyWashingMachineRemoteControlSensor(CandyRemoteControlBaseSensor, CandyWashingMachineBaseSensor):

    @property
    def state(self) -> StateType:
        status: WashingMachineStatus = self.coordinator.data
        return status.remote_control
