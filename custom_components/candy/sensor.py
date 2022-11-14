from abc import abstractmethod
from typing import Any, Mapping

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import TEMP_CELSIUS, TIME_MINUTES
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import (CoordinatorEntity,
                                                      DataUpdateCoordinator)

from .client import WashingMachineStatus
from .client.model import (DishwasherState, DishwasherStatus,
                           DryerProgramState, MachineState, OvenStatus,
                           TumbleDryerStatus)
from .const import *


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
    """Set up the Candy sensors from config entry."""

    config_id = config_entry.entry_id
    coordinator = hass.data[DOMAIN][config_id][DATA_KEY_COORDINATOR]

    if isinstance(coordinator.data, WashingMachineStatus):
        async_add_entities([
            CandyWashingMachineSensor(coordinator, config_id),
            CandyWashCycleStatusSensor(coordinator, config_id),
            CandyWashRemainingTimeSensor(coordinator, config_id)
        ])
    elif isinstance(coordinator.data, TumbleDryerStatus):
        async_add_entities([
            CandyTumbleDryerSensor(coordinator, config_id),
            CandyTumbleStatusSensor(coordinator, config_id),
            CandyTumbleRemainingTimeSensor(coordinator, config_id)
        ])
    elif isinstance(coordinator.data, OvenStatus):
        async_add_entities([
            CandyOvenSensor(coordinator, config_id),
            CandyOvenTempSensor(coordinator, config_id)
        ])
    elif isinstance(coordinator.data, DishwasherStatus):
        async_add_entities([
            CandyDishwasherSensor(coordinator, config_id),
            CandyDishwasherRemainingTimeSensor(coordinator, config_id)
        ])
    else:
        raise Exception(f"Unable to determine machine type: {coordinator.data}")


class CandyBaseSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator: DataUpdateCoordinator, config_id: str):
        super().__init__(coordinator)
        self.config_id = config_id

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.config_id)},
            name=self.device_name(),
            manufacturer="Candy",
            suggested_area=self.suggested_area(),
        )

    @abstractmethod
    def device_name(self) -> str:
        pass

    @abstractmethod
    def suggested_area(self) -> str:
        pass


class CandyWashingMachineSensor(CandyBaseSensor):

    def device_name(self) -> str:
        return DEVICE_NAME_WASHING_MACHINE

    def suggested_area(self) -> str:
        return SUGGESTED_AREA_BATHROOM

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
            "remaining_minutes": status.remaining_minutes if status.machine_state in [MachineState.RUNNING,
                                                                                      MachineState.PAUSED] else 0,
            "remote_control": status.remote_control,
        }

        if status.fill_percent is not None:
            attributes["fill_percent"] = status.fill_percent

        if status.program_code is not None:
            attributes["program_code"] = status.program_code

        return attributes


class CandyWashCycleStatusSensor(CandyBaseSensor):

    def device_name(self) -> str:
        return DEVICE_NAME_WASHING_MACHINE

    def suggested_area(self) -> str:
        return SUGGESTED_AREA_BATHROOM

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


class CandyWashRemainingTimeSensor(CandyBaseSensor):

    def device_name(self) -> str:
        return DEVICE_NAME_WASHING_MACHINE

    def suggested_area(self) -> str:
        return SUGGESTED_AREA_BATHROOM

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
        return TIME_MINUTES

    @property
    def icon(self) -> str:
        return "mdi:progress-clock"


class CandyTumbleDryerSensor(CandyBaseSensor):

    def device_name(self) -> str:
        return DEVICE_NAME_TUMBLE_DRYER

    def suggested_area(self) -> str:
        return SUGGESTED_AREA_BATHROOM

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


class CandyTumbleStatusSensor(CandyBaseSensor):

    def device_name(self) -> str:
        return DEVICE_NAME_TUMBLE_DRYER

    def suggested_area(self) -> str:
        return SUGGESTED_AREA_BATHROOM

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


class CandyTumbleRemainingTimeSensor(CandyBaseSensor):

    def device_name(self) -> str:
        return DEVICE_NAME_TUMBLE_DRYER

    def suggested_area(self) -> str:
        return SUGGESTED_AREA_BATHROOM

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
        return TIME_MINUTES

    @property
    def icon(self) -> str:
        return "mdi:progress-clock"


class CandyOvenSensor(CandyBaseSensor):

    def device_name(self) -> str:
        return DEVICE_NAME_OVEN

    def suggested_area(self) -> str:
        return SUGGESTED_AREA_KITCHEN

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


class CandyOvenTempSensor(CandyBaseSensor):

    def device_name(self) -> str:
        return DEVICE_NAME_OVEN

    def suggested_area(self) -> str:
        return SUGGESTED_AREA_KITCHEN

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
        return TEMP_CELSIUS

    @property
    def icon(self) -> str:
        return "mdi:thermometer"


class CandyDishwasherSensor(CandyBaseSensor):

    def device_name(self) -> str:
        return DEVICE_NAME_DISHWASHER

    def suggested_area(self) -> str:
        return SUGGESTED_AREA_KITCHEN

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
            "remaining_minutes": 0 if status.machine_state in
                                      [DishwasherState.IDLE, DishwasherState.FINISHED] else status.remaining_minutes,
            "remote_control": status.remote_control,
            "door_open": status.door_open,
            "eco_mode": status.eco_mode,
            "salt_empty": status.salt_empty,
            "rinse_aid_empty": status.rinse_aid_empty
        }

        if status.door_open_allowed is not None:
            attributes["door_open_allowed"] = status.door_open_allowed

        if status.delayed_start_hours is not None:
            attributes["delayed_start_hours"] = status.delayed_start_hours

        return attributes


class CandyDishwasherRemainingTimeSensor(CandyBaseSensor):

    def device_name(self) -> str:
        return DEVICE_NAME_DISHWASHER

    def suggested_area(self) -> str:
        return SUGGESTED_AREA_KITCHEN

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
        return TIME_MINUTES

    @property
    def icon(self) -> str:
        return "mdi:progress-clock"
