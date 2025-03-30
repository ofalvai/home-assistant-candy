from typing import Any, Mapping

from homeassistant.const import UnitOfTime
from homeassistant.helpers.typing import StateType

from ..const import *
from ..client.model import DishwasherState, DishwasherStatus

from . import CandyBaseSensor, CandyRemoteControlBaseSensor


class CandyDishwasherBaseSensor(CandyBaseSensor):

    def device_name(self) -> str:
        return DEVICE_NAME_DISHWASHER

    def suggested_area(self) -> str:
        return SUGGESTED_AREA_KITCHEN


class CandyDishwasherSensor(CandyDishwasherBaseSensor):

    @property
    def name(self) -> str:
        return self.device_name()

    @property
    def unique_id(self) -> str:
        return UNIQUE_ID_DISHWASHER.format(self.config_id)

    @property
    def state(self) -> StateType:
        status: DishwasherStatus = self.coordinator.data
        return str(status.machine_state)

    @property
    def icon(self) -> str:
        return "mdi:glass-wine"

    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        status: DishwasherStatus = self.coordinator.data

        attributes = {
            "program": status.program,
            "remaining_minutes": (
                0
                if status.machine_state
                in [DishwasherState.IDLE, DishwasherState.FINISHED]
                else status.remaining_minutes
            ),
            "door_open": status.door_open,
            "eco_mode": status.eco_mode,
            "salt_empty": status.salt_empty,
            "rinse_aid_empty": status.rinse_aid_empty,
        }

        if status.door_open_allowed is not None:
            attributes["door_open_allowed"] = status.door_open_allowed

        if status.delayed_start_hours is not None:
            attributes["delayed_start_hours"] = status.delayed_start_hours

        return attributes


class CandyDishwasherRemainingTimeSensor(CandyDishwasherBaseSensor):

    @property
    def name(self) -> str:
        return "Dishwasher remaining time"

    @property
    def unique_id(self) -> str:
        return UNIQUE_ID_DISHWASHER_REMAINING_TIME.format(self.config_id)

    @property
    def state(self) -> StateType:
        status: DishwasherStatus = self.coordinator.data
        if status.machine_state in [DishwasherState.IDLE, DishwasherState.FINISHED]:
            return 0
        else:
            return status.remaining_minutes

    @property
    def unit_of_measurement(self) -> str:
        return UnitOfTime.MINUTES

    @property
    def icon(self) -> str:
        return "mdi:progress-clock"


class CandyDishwasherRemoteControlSensor(CandyRemoteControlBaseSensor, CandyDishwasherBaseSensor):

    @property
    def state(self) -> StateType:
        status: DishwasherStatus = self.coordinator.data
        return status.remote_control
