from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .client.model import (
    DishwasherStatus,
    OvenStatus,
    TumbleDryerStatus,
    WashingMachineStatus
)
from .const import *
from .sensors.washing_machine import (
    CandyWashingMachineSensor,
    CandyWashingMachineCycleStatusSensor,
    CandyWashingMachineRemainingTimeSensor,
    CandyWashingMachineRemoteControlSensor
)
from .sensors.tumble_dryer import (
    CandyTumbleDryerSensor,
    CandyTumbleDryerStatusSensor,
    CandyTumbleDryerRemainingTimeSensor,
    CandyTumbleDryerRemoteControlSensor
)
from .sensors.oven import (
    CandyOvenSensor,
    CandyOvenTempSensor,
    CandyOvenRemoteControlSensor
)
from .sensors.dish_washer import (
    CandyDishwasherSensor,
    CandyDishwasherRemainingTimeSensor,
    CandyDishwasherRemoteControlSensor
)



async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
    """Set up the Candy sensors from config entry."""

    config_id = config_entry.entry_id
    coordinator = hass.data[DOMAIN][config_id][DATA_KEY_COORDINATOR]

    if isinstance(coordinator.data, WashingMachineStatus):
        async_add_entities([
            CandyWashingMachineSensor(coordinator, config_id),
            CandyWashingMachineCycleStatusSensor(coordinator, config_id),
            CandyWashingMachineRemainingTimeSensor(coordinator, config_id),
            CandyWashingMachineRemoteControlSensor(coordinator, config_id)
        ])
    elif isinstance(coordinator.data, TumbleDryerStatus):
        async_add_entities([
            CandyTumbleDryerSensor(coordinator, config_id),
            CandyTumbleDryerStatusSensor(coordinator, config_id),
            CandyTumbleDryerRemainingTimeSensor(coordinator, config_id),
            CandyTumbleDryerRemoteControlSensor(coordinator, config_id)
        ])
    elif isinstance(coordinator.data, OvenStatus):
        async_add_entities([
            CandyOvenSensor(coordinator, config_id),
            CandyOvenTempSensor(coordinator, config_id),
            CandyOvenRemoteControlSensor(coordinator, config_id)
        ])
    elif isinstance(coordinator.data, DishwasherStatus):
        async_add_entities([
            CandyDishwasherSensor(coordinator, config_id),
            CandyDishwasherRemainingTimeSensor(coordinator, config_id),
            CandyDishwasherRemoteControlSensor(coordinator, config_id)
        ])
    else:
        raise Exception(f"Unable to determine machine type: {coordinator.data}")
