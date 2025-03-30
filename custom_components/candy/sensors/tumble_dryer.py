from typing import Any, Mapping

from homeassistant.const import UnitOfTime

from homeassistant.helpers.typing import StateType

from ..const import *
from ..client.model import DryerProgramState, DryerProgramState, MachineState, TumbleDryerStatus
from . import CandyBaseSensor, CandyRemoteControlBaseSensor


class CandyTumbleDryerBaseSensor(CandyBaseSensor):

    def device_name(self) -> str:
        return DEVICE_NAME_TUMBLE_DRYER

    def suggested_area(self) -> str:
        return SUGGESTED_AREA_BATHROOM


class CandyTumbleDryerSensor(CandyTumbleDryerBaseSensor):

    @property
    def name(self) -> str:
        return self.device_name()

    @property
    def unique_id(self) -> str:
        return UNIQUE_ID_TUMBLE_DRYER.format(self.config_id)

    @property
    def state(self) -> StateType:
        status: TumbleDryerStatus = self.coordinator.data
        return str(status.machine_state)

    @property
    def icon(self) -> str:
        return "mdi:tumble-dryer"

    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        status: TumbleDryerStatus = self.coordinator.data

        attributes = {
            "program": status.program,
            "remaining_minutes": status.remaining_minutes,
            "remote_control": status.remote_control,
            "dry_level": status.dry_level,
            "dry_level_now": status.dry_level_selected,
            "refresh": status.refresh,
            "need_clean_filter": status.need_clean_filter,
            "water_tank_full": status.water_tank_full,
            "door_closed": status.door_closed,
        }

        return attributes


class CandyTumbleDryerStatusSensor(CandyTumbleDryerBaseSensor):

    @property
    def name(self) -> str:
        return "Dryer cycle status"

    @property
    def unique_id(self) -> str:
        return UNIQUE_ID_TUMBLE_CYCLE_STATUS.format(self.config_id)

    @property
    def state(self) -> StateType:
        status: TumbleDryerStatus = self.coordinator.data
        if status.program_state in [DryerProgramState.STOPPED]:
            return str(status.cycle_state)
        else:
            return str(status.program_state)

    @property
    def icon(self) -> str:
        return "mdi:tumble-dryer"


class CandyTumbleDryerRemainingTimeSensor(CandyTumbleDryerBaseSensor):

    @property
    def name(self) -> str:
        return "Dryer cycle remaining time"

    @property
    def unique_id(self) -> str:
        return UNIQUE_ID_TUMBLE_REMAINING_TIME.format(self.config_id)

    @property
    def state(self) -> StateType:
        status: TumbleDryerStatus = self.coordinator.data
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


class CandyTumbleDryerRemoteControlSensor(CandyRemoteControlBaseSensor, CandyTumbleDryerBaseSensor):

    @property
    def state(self) -> StateType:
        status: TumbleDryerStatus = self.coordinator.data
        return status.remote_control
