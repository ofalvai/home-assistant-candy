from abc import abstractmethod
from typing import Mapping, Any

from homeassistant.helpers.typing import StateType
from .client import WashingMachineStatus
from .client.model import MachineState, TumbleDryerStatus
from .const import *
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import TIME_MINUTES
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator
from homeassistant.helpers.entity import DeviceInfo


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
    """Set up the Candy sensors from config entry."""

    config_id = config_entry.entry_id
    coordinator = hass.data[DOMAIN][config_id][DATA_KEY_COORDINATOR]

    if type(coordinator.data) is WashingMachineStatus:
        async_add_entities([
            CandyWashingMachineSensor(coordinator, config_id),
            CandyWashCycleStatusSensor(coordinator, config_id),
            CandyWashRemainingTimeSensor(coordinator, config_id)
        ])
    elif type(coordinator.data) is TumbleDryerStatus:
        async_add_entities([
            CandyTumbleDryerSensor(coordinator, config_id)
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
            suggested_area="Bathroom",
        )

    @abstractmethod
    def device_name(self) -> str:
        pass


class CandyWashingMachineSensor(CandyBaseSensor):

    def device_name(self) -> str:
        return DEVICE_NAME_WASHING_MACHINE

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
            "remaining_minutes": status.remaining_minutes,
            "remote_control": status.remote_control,
        }

        if status.fill_percent is not None:
            attributes["fill_percent"] = status.fill_percent

        return attributes


class CandyWashCycleStatusSensor(CandyBaseSensor):

    def device_name(self) -> str:
        return DEVICE_NAME_WASHING_MACHINE

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
            "machine_state": str(status.machine_state),
            "program_state": str(status.program_state),
            "dry_level_state": str(status.dry_level_state),
            "remaining_minutes": status.remaining_minutes,
            "remote_control": status.remote_control,
            "water_tank_full": status.water_tank_full,
            "clean_filter": status.clean_filter
        }

        return attributes
