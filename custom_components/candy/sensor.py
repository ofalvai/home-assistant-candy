from typing import Optional, Mapping, Any

from homeassistant.helpers.typing import StateType
from .client import MachineStatus
from .client.model import MachineState
from .const import *
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import TIME_MINUTES
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
    """Set up the Candy sensors from config entry."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id][DATA_KEY_COORDINATOR]

    async_add_entities([
        CandyWashingMachineSensor(coordinator),
        CandyCycleStatusSensor(coordinator),
        CandyRemainingTimeSensor(coordinator)
    ])


# TODO: unique ID
class CandyWashingMachineSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)

    @property
    def name(self) -> str:
        return "Washing machine"

    @property
    def state(self) -> StateType:
        status: MachineStatus = self.coordinator.data
        return str(status.machine_state)

    @property
    def icon(self) -> str:
        return "mdi:washing-machine"

    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        status: MachineStatus = self.coordinator.data

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


# TODO: unique ID
class CandyCycleStatusSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)

    @property
    def name(self) -> str:
        return "Wash cycle status"

    @property
    def state(self) -> StateType:
        status: MachineStatus = self.coordinator.data
        return str(status.program_state)

    @property
    def icon(self) -> str:
        return "mdi:washing-machine"


# TODO: unique ID
class CandyRemainingTimeSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)

    @property
    def name(self) -> str:
        return "Wash cycle remaining time"

    @property
    def state(self) -> StateType:
        status: MachineStatus = self.coordinator.data
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
