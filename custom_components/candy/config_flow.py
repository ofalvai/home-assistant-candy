"""Config flow for GreenGo integration."""
from __future__ import annotations

import logging
from typing import Any

import async_timeout
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_IP_ADDRESS, CONF_PASSWORD
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .client import detect_encryption
from .client.decryption import Encryption
from .const import *

_LOGGER = logging.getLogger(__name__)

STEP_DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_IP_ADDRESS): str,
})


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Candy."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(
            self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=STEP_DATA_SCHEMA)

        config_data = {
            CONF_IP_ADDRESS: user_input[CONF_IP_ADDRESS]
        }

        errors = {}
        try:
            async with async_timeout.timeout(40):
                encryption_type, key = await detect_encryption(
                    session=async_get_clientsession(self.hass),
                    device_ip=user_input[CONF_IP_ADDRESS]
                )
        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.exception(err)
            errors["base"] = "detect_encryption"
        else:
            if encryption_type == Encryption.ENCRYPTION:
                config_data[CONF_KEY_USE_ENCRYPTION] = True
                config_data[CONF_PASSWORD] = key
            elif encryption_type == Encryption.NO_ENCRYPTION:
                config_data[CONF_KEY_USE_ENCRYPTION] = False
            elif encryption_type == Encryption.ENCRYPTION_WITHOUT_KEY:
                config_data[CONF_KEY_USE_ENCRYPTION] = True
                config_data[CONF_PASSWORD] = ""

            return self.async_create_entry(title=CONF_INTEGRATION_TITLE, data=config_data)

        return self.async_show_form(
            step_id="user", data_schema=STEP_DATA_SCHEMA, errors=errors
        )
