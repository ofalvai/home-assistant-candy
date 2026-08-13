"""The Candy integration."""
from __future__ import annotations

import logging
from datetime import timedelta

import async_timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_IP_ADDRESS, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .client import CandyClient, WashingMachineStatus
from .client.model import (DishwasherState, DishwasherStatus, DryerProgramState,
                           MachineState, OvenState, OvenStatus,
                           TumbleDryerStatus)

from .const import *

_LOGGER = logging.getLogger(__name__)

ACTIVE_UPDATE_INTERVAL = timedelta(seconds=60)
IDLE_UPDATE_INTERVAL = timedelta(minutes=15)


def _is_idle_or_finished(status) -> bool:
    """Return whether an appliance is likely to disconnect from Wi-Fi."""
    if isinstance(status, WashingMachineStatus):
        return status.machine_state in {
            MachineState.IDLE,
            MachineState.FINISHED1,
            MachineState.FINISHED2,
        }
    if isinstance(status, TumbleDryerStatus):
        return status.program_state in {
            DryerProgramState.STOPPED,
            DryerProgramState.END,
        }
    if isinstance(status, DishwasherStatus):
        return status.machine_state in {
            DishwasherState.IDLE,
            DishwasherState.FINISHED,
        }
    if isinstance(status, OvenStatus):
        return status.machine_state is OvenState.IDLE
    return False


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up Candy from a config entry."""

    ip_address = config_entry.data[CONF_IP_ADDRESS]
    encryption_key = config_entry.data.get(CONF_PASSWORD, "")
    use_encryption = config_entry.data.get(CONF_KEY_USE_ENCRYPTION, True)

    session = async_get_clientsession(hass)
    client = CandyClient(session, ip_address, encryption_key, use_encryption)
    last_status = None

    async def update_status():
        nonlocal last_status
        try:
            async with async_timeout.timeout(40):
                status = await client.status_with_retry()
                _LOGGER.debug("Fetched status: %s", status)
                last_status = status
                coordinator.update_interval = (
                    IDLE_UPDATE_INTERVAL
                    if _is_idle_or_finished(status)
                    else ACTIVE_UPDATE_INTERVAL
                )
                return status
        except Exception as err:
            if last_status is not None and _is_idle_or_finished(last_status):
                _LOGGER.debug(
                    "Appliance is unavailable after reaching an idle or finished state; "
                    "keeping the last known status"
                )
                return last_status
            raise UpdateFailed(f"Error communicating with API: {repr(err)}") from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_interval=ACTIVE_UPDATE_INTERVAL,
        update_method=update_status,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[config_entry.entry_id] = {
        DATA_KEY_COORDINATOR: coordinator
    }

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        del hass.data[DOMAIN]

    return unload_ok
