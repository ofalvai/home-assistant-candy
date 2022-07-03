from abc import abstractmethod
from typing import Mapping, Any

from homeassistant.helpers.typing import StateType
from .client import WashingMachineStatus
from .client.model import (
    FridgeStatus,
    HobHeaterStatus,
    HobState,
    HobStatus,
    HoodStatus,
    MachineState,
    TumbleDryerStatus,
    DryerProgramState,
    OvenStatus,
    DishwasherStatus,
    DishwasherState,
)
from .const import *
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import TIME_MINUTES, TEMP_CELSIUS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from homeassistant.helpers.entity import DeviceInfo


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities
):
    """Set up the Candy sensors from config entry."""

    config_id = config_entry.entry_id
    coordinator = hass.data[DOMAIN][config_id][DATA_KEY_COORDINATOR]

    if type(coordinator.data) is WashingMachineStatus:
        async_add_entities(
            [
                CandyWashingMachineSensor(coordinator, config_id),
                CandyWashCycleStatusSensor(coordinator, config_id),
                CandyWashRemainingTimeSensor(coordinator, config_id),
            ]
        )
    elif type(coordinator.data) is TumbleDryerStatus:
        async_add_entities(
            [
                CandyTumbleDryerSensor(coordinator, config_id),
                CandyTumbleStatusSensor(coordinator, config_id),
                CandyTumbleRemainingTimeSensor(coordinator, config_id),
            ]
        )
    elif type(coordinator.data) is OvenStatus:
        async_add_entities(
            [
                CandyOvenSensor(coordinator, config_id),
                CandyOvenTempSensor(coordinator, config_id),
                CandyOvenSetTempSensor(coordinator, config_id),
            ]
        )
    elif type(coordinator.data) is HoodStatus:
        async_add_entities(
            [
                CandyHoodSensor(coordinator, config_id)
            ]
        )
    elif type(coordinator.data) is FridgeStatus:
        async_add_entities(
            [
                CandyFridgeSensor(coordinator, config_id),
                CandyFridgeCoolingTempSensor(coordinator, config_id),
                CandyFridgeFreezingTempSensor(coordinator, config_id),
            ]
        )
    elif type(coordinator.data) is HobStatus:
        if coordinator.data.heater4 is not None:
            async_add_entities(
                [
                    CandyHobSensor(coordinator, config_id),
                    CandyHobHeater1Sensor(coordinator, config_id),
                    CandyHobHeater2Sensor(coordinator, config_id),
                    CandyHobHeater3Sensor(coordinator, config_id),
                    CandyHobHeater4Sensor(coordinator, config_id),
                ]
            )
        elif coordinator.data.heater3 is not None:
            async_add_entities(
                [
                    CandyHobSensor(coordinator, config_id),
                    CandyHobHeater1Sensor(coordinator, config_id),
                    CandyHobHeater2Sensor(coordinator, config_id),
                    CandyHobHeater3Sensor(coordinator, config_id),
                ]
            )
        elif coordinator.data.heater2 is not None:
            async_add_entities(
                [
                    CandyHobSensor(coordinator, config_id),
                    CandyHobHeater1Sensor(coordinator, config_id),
                    CandyHobHeater2Sensor(coordinator, config_id),
                ]
            )
        elif coordinator.data.heater1 is not None:
            async_add_entities(
                [
                    CandyHobSensor(coordinator, config_id),
                    CandyHobHeater1Sensor(coordinator, config_id),
                ]
            )
    elif type(coordinator.data) is DishwasherStatus:
        async_add_entities(
            [
                CandyDishwasherSensor(coordinator, config_id),
                CandyDishwasherRemainingTimeSensor(coordinator, config_id),
            ]
        )
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
            "remaining_minutes": status.remaining_minutes
            if status.machine_state in [MachineState.RUNNING, MachineState.PAUSED]
            else 0,
            "remote_control": status.remote_control,
        }

        if status.fill_percent is not None:
            attributes["fill_percent"] = status.fill_percent

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
            "temp_set": status.tempSet,
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


class CandyOvenSetTempSensor(CandyBaseSensor):
    def device_name(self) -> str:
        return DEVICE_NAME_OVEN

    def suggested_area(self) -> str:
        return SUGGESTED_AREA_KITCHEN

    @property
    def name(self) -> str:
        return "Oven set temperature"

    @property
    def unique_id(self) -> str:
        return UNIQUE_ID_OVEN_SET_TEMP.format(self.config_id)

    @property
    def state(self) -> StateType:
        status: OvenStatus = self.coordinator.data
        return status.tempSet

    @property
    def unit_of_measurement(self) -> str:
        return TEMP_CELSIUS

    @property
    def icon(self) -> str:
        return "mdi:thermometer"


class CandyHobSensor(CandyBaseSensor):
    def device_name(self) -> str:
        return DEVICE_NAME_HOB

    def suggested_area(self) -> str:
        return SUGGESTED_AREA_KITCHEN

    @property
    def name(self) -> str:
        return self.device_name()

    @property
    def unique_id(self) -> str:
        return UNIQUE_ID_HOB.format(self.config_id)

    @property
    def state(self) -> StateType:
        status: HobStatus = self.coordinator.data
        return str(status.machine_state)

    @property
    def icon(self) -> str:
        return "mdi:pot-steam"

    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        status: HobStatus = self.coordinator.data

        attributes = {
            "lock": status.lock,
            "remote_control": status.remote_control,
        }

        return attributes


class CandyHobHeater1Sensor(CandyBaseSensor):
    def device_name(self) -> str:
        return DEVICE_NAME_HOB

    def suggested_area(self) -> str:
        return SUGGESTED_AREA_KITCHEN

    @property
    def name(self) -> str:
        return DEVICE_NAME_HOB_HEATER.format("1")

    @property
    def unique_id(self) -> str:
        return UNIQUE_ID_HOB_HEATER.format(self.config_id, "1")

    @property
    def state(self) -> StateType:
        status: HobStatus = self.coordinator.data

        return str(status.heater1.heater_state) + " (" + str(status.heater1.power) + ")"

    @property
    def unit_of_measurement(self) -> str:
        return ""

    @property
    def icon(self) -> str:
        status: HobStatus = self.coordinator.data
        if status.heater1.heater_state != HobState.IDLE:
            return "mdi:circle-slice-8"
        else:
            return "mdi:circle-outline"

    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        status: HobStatus = self.coordinator.data

        attributes = {
            "heater_state": status.heater1.heater_state,
            "status": status.heater1.status,
            "pan": status.heater1.pan,
            "combi": status.heater1.combi,
            "hot": status.heater1.hot,
            "low": status.heater1.low,
            "power": status.heater1.power,
        }

        if status.heater1.timer_minutes is not None:
            attributes["timer_minutes"] = status.heater1.timer_minutes

        return attributes


class CandyHobHeater2Sensor(CandyBaseSensor):
    def device_name(self) -> str:
        return DEVICE_NAME_HOB

    def suggested_area(self) -> str:
        return SUGGESTED_AREA_KITCHEN

    @property
    def name(self) -> str:
        return DEVICE_NAME_HOB_HEATER.format("2")

    @property
    def unique_id(self) -> str:
        return UNIQUE_ID_HOB_HEATER.format(self.config_id, "2")

    @property
    def state(self) -> StateType:
        status: HobStatus = self.coordinator.data

        return str(status.heater2.heater_state) + " (" + str(status.heater2.power) + ")"

    @property
    def unit_of_measurement(self) -> str:
        return ""

    @property
    def icon(self) -> str:
        status: HobStatus = self.coordinator.data
        if status.heater2.heater_state != HobState.IDLE:
            return "mdi:circle-slice-8"
        else:
            return "mdi:circle-outline"

    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        status: HobStatus = self.coordinator.data

        attributes = {
            "heater_state": status.heater2.heater_state,
            "status": status.heater2.status,
            "pan": status.heater2.pan,
            "combi": status.heater2.combi,
            "hot": status.heater2.hot,
            "low": status.heater2.low,
            "power": status.heater2.power,
        }

        if status.heater2.timer_minutes is not None:
            attributes["timer_minutes"] = status.heater2.timer_minutes

        return attributes


class CandyHobHeater3Sensor(CandyBaseSensor):
    def device_name(self) -> str:
        return DEVICE_NAME_HOB

    def suggested_area(self) -> str:
        return SUGGESTED_AREA_KITCHEN

    @property
    def name(self) -> str:
        return DEVICE_NAME_HOB_HEATER.format("3")

    @property
    def unique_id(self) -> str:
        return UNIQUE_ID_HOB_HEATER.format(self.config_id, "31")

    @property
    def state(self) -> StateType:
        status: HobStatus = self.coordinator.data

        return str(status.heater3.heater_state) + " (" + str(status.heater3.power) + ")"

    @property
    def unit_of_measurement(self) -> str:
        return ""

    @property
    def icon(self) -> str:
        status: HobStatus = self.coordinator.data
        if status.heater3.heater_state != HobState.IDLE:
            return "mdi:circle-slice-8"
        else:
            return "mdi:circle-outline"

    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        status: HobStatus = self.coordinator.data

        attributes = {
            "heater_state": status.heater3.heater_state,
            "status": status.heater3.status,
            "pan": status.heater3.pan,
            "combi": status.heater3.combi,
            "hot": status.heater3.hot,
            "low": status.heater3.low,
            "power": status.heater3.power,
        }

        if status.heater1.timer_minutes is not None:
            attributes["timer_minutes"] = status.heater3.timer_minutes

        return attributes


class CandyHobHeater4Sensor(CandyBaseSensor):
    def device_name(self) -> str:
        return DEVICE_NAME_HOB

    def suggested_area(self) -> str:
        return SUGGESTED_AREA_KITCHEN

    @property
    def name(self) -> str:
        return DEVICE_NAME_HOB_HEATER.format("4")

    @property
    def unique_id(self) -> str:
        return UNIQUE_ID_HOB_HEATER.format(self.config_id, "4")

    @property
    def state(self) -> StateType:
        status: HobStatus = self.coordinator.data

        return str(status.heater4.heater_state) + " (" + str(status.heater4.power) + ")"

    @property
    def unit_of_measurement(self) -> str:
        return ""

    @property
    def icon(self) -> str:
        status: HobStatus = self.coordinator.data
        if status.heater4.heater_state != HobState.IDLE:
           return "mdi:circle-slice-8"
        else:
            return "mdi:circle-outline"

    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        status: HobStatus = self.coordinator.data

        attributes = {
            "heater_state": status.heater4.heater_state,
            "status": status.heater4.status,
            "pan": status.heater4.pan,
            "combi": status.heater4.combi,
            "hot": status.heater4.hot,
            "low": status.heater4.low,
            "power": status.heater4.power,
        }

        if status.heater1.timer_minutes is not None:
            attributes["timer_minutes"] = status.heater4.timer_minutes

        return attributes


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
            "remaining_minutes": 0
            if status.machine_state in [DishwasherState.IDLE, DishwasherState.FINISHED]
            else status.remaining_minutes,
            "remote_control": status.remote_control,
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


class CandyHoodSensor(CandyBaseSensor):
    def device_name(self) -> str:
        return DEVICE_NAME_HOOD

    def suggested_area(self) -> str:
        return SUGGESTED_AREA_KITCHEN

    @property
    def name(self) -> str:
        return self.device_name()

    @property
    def unique_id(self) -> str:
        return UNIQUE_ID_HOOD.format(self.config_id)

    @property
    def state(self) -> StateType:
        status: HoodStatus = self.coordinator.data
        return str(status.machine_state)

    @property
    def icon(self) -> str:
        return "mdi:fan"

    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        status: HoodStatus = self.coordinator.data

        attributes = {
            "lock": status.lock,
            "light": status.light,
            "fan": status.fan,
            "grease_filter": status.grease_filter,
            "carbon_Filter": status.carbon_Filter,
            "warning": status.warning,
            "remote_control": status.remote_control
        }

        return attributes

class CandyFridgeSensor(CandyBaseSensor):
    def device_name(self) -> str:
        return DEVICE_NAME_FRIDGE

    def suggested_area(self) -> str:
        return SUGGESTED_AREA_KITCHEN

    @property
    def name(self) -> str:
        return self.device_name()

    @property
    def unique_id(self) -> str:
        return UNIQUE_ID_FRIDGE.format(self.config_id)

    @property
    def state(self) -> StateType:
        status: FridgeStatus = self.coordinator.data
        return str(status.machine_state)

    @property
    def icon(self) -> str:
        return "mdi:fridge"

    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        status: FridgeStatus = self.coordinator.data

        attributes = {
            "cooling_temperature": status.cooling_temperature,
            "freezing_temperature": status.freezing_temperature,
            "eco_mode": status.eco_mode,
            "super_freezing_mode": status.super_freezing_mode,
            "smart_cooling_mode": status.smart_cooling_mode,
            "door_locked": status.door_locked,
            "door_open": status.door_open,
            "fan": status.fan,
            "remote_control": status.remote_control,
        }

        if status.error is not None:
            attributes["error"] = status.error

        return attributes


class CandyFridgeCoolingTempSensor(CandyBaseSensor):
    def device_name(self) -> str:
        return DEVICE_NAME_FRIDGE

    def suggested_area(self) -> str:
        return SUGGESTED_AREA_KITCHEN

    @property
    def name(self) -> str:
        return "Cooling temperature"

    @property
    def unique_id(self) -> str:
        return UNIQUE_ID_FRIDGE_COOLING_TEMP.format(self.config_id)

    @property
    def state(self) -> StateType:
        status: FridgeStatus = self.coordinator.data
        return status.cooling_temperature

    @property
    def unit_of_measurement(self) -> str:
        return TEMP_CELSIUS

    @property
    def icon(self) -> str:
        return "mdi:thermometer"


class CandyFridgeFreezingTempSensor(CandyBaseSensor):
    def device_name(self) -> str:
        return DEVICE_NAME_FRIDGE

    def suggested_area(self) -> str:
        return SUGGESTED_AREA_KITCHEN

    @property
    def name(self) -> str:
        return "Freezing temperature"

    @property
    def unique_id(self) -> str:
        return UNIQUE_ID_FRIDGE_FREEZING_TEMP.format(self.config_id)

    @property
    def state(self) -> StateType:
        status: FridgeStatus = self.coordinator.data
        return status.freezing_temperature

    @property
    def unit_of_measurement(self) -> str:
        return TEMP_CELSIUS

    @property
    def icon(self) -> str:
        return "mdi:thermometer"