from abc import abstractmethod
from typing import Mapping, Any

from homeassistant.helpers.typing import StateType
from .client import WashingMachineStatus
from .client.model import (
    FridgeState,
    FridgeStatus,
    HobHeaterStatus,
    HobState,
    HobStatus,
    HoodState,
    HoodStatus,
    MachineState,
    OvenState,
    TumbleDryerStatus,
    DryerProgramState,
    OvenStatus,
    DishwasherStatus,
    DishwasherState,
)
from .const import *
from homeassistant.components.binary_sensor import BinarySensorEntity
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
                CandyWashingMachineBinarySensor(coordinator, config_id)
            ]
        )
    elif type(coordinator.data) is TumbleDryerStatus:
        async_add_entities(
            [
                CandyTumbleDryerBinarySensor(coordinator, config_id)
            ]
        )
    elif type(coordinator.data) is OvenStatus:
        async_add_entities(
            [
                CandyOvenBinarySensor(coordinator, config_id)
            ]
        )
    elif type(coordinator.data) is HoodStatus:
        async_add_entities(
            [
                CandyHoodBinarySensor(coordinator, config_id)
            ]
        )
    elif type(coordinator.data) is FridgeStatus:
        async_add_entities(
            [
                CandyFridgeBinarySensor(coordinator, config_id)
            ]
        )
    elif type(coordinator.data) is HobStatus:
        async_add_entities(
            [
                CandyHobBinarySensor(coordinator, config_id)
            ]
        )                
    elif type(coordinator.data) is DishwasherStatus:
        async_add_entities(
            [
                CandyDishwasherBinarySensor(coordinator, config_id)
            ]
        )
    else:
        raise Exception(f"Unable to determine machine type: {coordinator.data}")


class CandyBaseBinarySensor(CoordinatorEntity, BinarySensorEntity):
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


class CandyWashingMachineBinarySensor(CandyBaseBinarySensor):

    def device_name(self) -> str:
        return DEVICE_NAME_WASHING_MACHINE

    def suggested_area(self) -> str:
        return SUGGESTED_AREA_BATHROOM

    @property
    def name(self) -> str:
        return self.device_name()

    @property
    def unique_id(self) -> str:
        return UNIQUE_ID_WASHING_MACHINE_BINARY.format(self.config_id)

    @property
    def state(self) -> StateType:
        status: WashingMachineStatus = self.coordinator.data
        return str(status.machine_state)

    @property
    def icon(self) -> str:
        return "mdi:washing-machine"

    @property
    def available(self):
        status: WashingMachineStatus = self.coordinator.data
        return status is not None

    @property
    def is_on(self):
        status: WashingMachineStatus = self.coordinator.data
        return status.machine_state not in [MachineState.IDLE] 


class CandyTumbleDryerBinarySensor(CandyBaseBinarySensor):
    def device_name(self) -> str:
        return DEVICE_NAME_TUMBLE_DRYER

    def suggested_area(self) -> str:
        return SUGGESTED_AREA_BATHROOM

    @property
    def name(self) -> str:
        return self.device_name()

    @property
    def unique_id(self) -> str:
        return UNIQUE_ID_TUMBLE_DRYER_BINARY.format(self.config_id)


    @property
    def icon(self) -> str:
        return "mdi:tumble-dryer"

    @property
    def available(self):
        status: TumbleDryerStatus = self.coordinator.data
        return status is not None

    @property
    def is_on(self):
        status: TumbleDryerStatus = self.coordinator.data
        return status.machine_state not in [MachineState.IDLE] 



class CandyOvenBinarySensor(CandyBaseBinarySensor):
    def device_name(self) -> str:
        return DEVICE_NAME_OVEN

    def suggested_area(self) -> str:
        return SUGGESTED_AREA_KITCHEN

    @property
    def name(self) -> str:
        return self.device_name()

    @property
    def unique_id(self) -> str:
        return UNIQUE_ID_OVEN_BINARY.format(self.config_id)

    @property
    def icon(self) -> str:
        return "mdi:stove"

    @property
    def available(self):
        status: OvenStatus = self.coordinator.data
        return status is not None

    @property
    def is_on(self):
        status: OvenStatus = self.coordinator.data
        return status.machine_state not in [OvenState.IDLE] 


class CandyHobBinarySensor(CandyBaseBinarySensor):
    def device_name(self) -> str:
        return DEVICE_NAME_HOB

    def suggested_area(self) -> str:
        return SUGGESTED_AREA_KITCHEN

    @property
    def name(self) -> str:
        return self.device_name()

    @property
    def unique_id(self) -> str:
        return UNIQUE_ID_HOB_BINARY.format(self.config_id)

    @property
    def icon(self) -> str:
        return "mdi:pot-steam"

    @property
    def available(self):
        status: HobStatus = self.coordinator.data
        return status is not None

    @property
    def is_on(self):
        status: HobStatus = self.coordinator.data
        return status.machine_state not in [HobState.IDLE] 

class CandyDishwasherBinarySensor(CandyBaseBinarySensor):
    def device_name(self) -> str:
        return DEVICE_NAME_DISHWASHER

    def suggested_area(self) -> str:
        return SUGGESTED_AREA_KITCHEN

    @property
    def name(self) -> str:
        return self.device_name()

    @property
    def unique_id(self) -> str:
        return UNIQUE_ID_DISHWASHER_BINARY.format(self.config_id)

    @property
    def icon(self) -> str:
        return "mdi:glass-wine"

    @property
    def available(self):
        status: DishwasherStatus = self.coordinator.data
        return status is not None

    @property
    def is_on(self):
        status: DishwasherStatus = self.coordinator.data
        return status.machine_state not in [DishwasherState.IDLE] 

class CandyHoodBinarySensor(CandyBaseBinarySensor):
    def device_name(self) -> str:
        return DEVICE_NAME_HOOD

    def suggested_area(self) -> str:
        return SUGGESTED_AREA_KITCHEN

    @property
    def name(self) -> str:
        return self.device_name()

    @property
    def unique_id(self) -> str:
        return UNIQUE_ID_HOOD_BINARY.format(self.config_id)

    @property
    def icon(self) -> str:
        return "mdi:fan"

    @property
    def available(self):
        status: HoodStatus = self.coordinator.data
        return status is not None

    @property
    def is_on(self):
        status: HoodStatus = self.coordinator.data
        return status.machine_state not in [HoodState.IDLE] 

class CandyFridgeBinarySensor(CandyBaseBinarySensor):
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
    def icon(self) -> str:
        return "mdi:fridge"

    @property
    def available(self):
        status: FridgeStatus = self.coordinator.data
        return status is not None

    @property
    def is_on(self):
        status: FridgeStatus = self.coordinator.data
        return status is not None


