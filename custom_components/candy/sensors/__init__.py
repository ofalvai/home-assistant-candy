from abc import abstractmethod

from homeassistant.const import EntityCategory
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from custom_components.candy.const import *

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


class CandyRemoteControlBaseSensor(CandyBaseSensor):

    @property
    def name(self) -> str:
        return "Remote Control"

    @property
    def unique_id(self) -> str:
        return UNIQUE_ID_REMOTE_CONTROL.format(self.config_id)

    @abstractmethod
    def state(self) -> StateType:
        pass

    @property
    def icon(self) -> str:
        return "mdi:check-network-outline"

    @property
    def entity_category(self) -> EntityCategory:
        return EntityCategory.DIAGNOSTIC
