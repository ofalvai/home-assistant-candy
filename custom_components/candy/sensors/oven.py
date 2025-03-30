from typing import Any, Mapping

from homeassistant.const import UnitOfTemperature
from homeassistant.helpers.typing import StateType

from ..const import *
from ..client.model import OvenStatus

from . import CandyBaseSensor, CandyRemoteControlBaseSensor


class CandyOvenBaseSensor(CandyBaseSensor):

    def device_name(self) -> str:
        return DEVICE_NAME_OVEN

    def suggested_area(self) -> str:
        return SUGGESTED_AREA_KITCHEN


class CandyOvenSensor(CandyOvenBaseSensor):

    @property
    def name(self) -> str:
        return self.device_name()

    @property
    def unique_id(self) -> str:
        return UNIQUE_ID_OVEN.format(self.config_id)

    @property
    def state(self) -> StateType:
        status: OvenStatus = self.coordinator.data
        return str(status.machine_state)

    @property
    def icon(self) -> str:
        return "mdi:stove"

    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        status: OvenStatus = self.coordinator.data

        attributes = {
            "program": status.program,
            "selection": status.selection,
            "temperature": status.temp,
            "temperature_reached": status.temp_reached,
            "remote_control": status.remote_control,
        }

        if status.program_length_minutes is not None:
            attributes["program_length_minutes"] = status.program_length_minutes

        return attributes


class CandyOvenTempSensor(CandyOvenBaseSensor):

    @property
    def name(self) -> str:
        return "Oven temperature"

    @property
    def unique_id(self) -> str:
        return UNIQUE_ID_OVEN_TEMP.format(self.config_id)

    @property
    def state(self) -> StateType:
        status: OvenStatus = self.coordinator.data
        return status.temp

    @property
    def unit_of_measurement(self) -> str:
        return UnitOfTemperature.CELSIUS

    @property
    def icon(self) -> str:
        return "mdi:thermometer"


class CandyOvenRemoteControlSensor(CandyRemoteControlBaseSensor, CandyOvenBaseSensor):

    @property
    def state(self) -> StateType:
        status: OvenStatus = self.coordinator.data
        return status.remote_control
