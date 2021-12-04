from unittest.mock import patch

import pytest
from homeassistant import config_entries, data_entry_flow
from homeassistant.const import CONF_IP_ADDRESS, CONF_PASSWORD

from custom_components.candy import DOMAIN, CONF_KEY_USE_ENCRYPTION
from custom_components.candy.client import Encryption


# This fixture bypasses the actual setup of the integration
# since we only want to test the config flow. We test the
# actual functionality of the integration in other test modules.
@pytest.fixture(autouse=True)
def bypass_setup_fixture():
    """Prevent setup."""
    with patch(
            "custom_components.candy.async_setup_entry",
            return_value=True,
    ):
        yield


@pytest.fixture(name="detect_no_encryption", autouse=False)
def detect_no_encryption_fixture():
    with patch(
            "custom_components.candy.config_flow.detect_encryption",
            return_value=(Encryption.NO_ENCRYPTION, None)
    ):
        yield


@pytest.fixture(name="detect_encryption_find_key", autouse=False)
def detect_encryption_find_key_fixture():
    with patch(
            "custom_components.candy.config_flow.detect_encryption",
            return_value=(Encryption.ENCRYPTION, "testkey")
    ):
        yield


@pytest.fixture(name="detect_encryption_key_not_found", autouse=False)
def detect_encryption_key_not_found_fixture():
    with patch(
            "custom_components.candy.config_flow.detect_encryption",
            side_effect=ValueError
    ):
        yield


@pytest.fixture(name="detect_encryption_without_key", autouse=False)
def detect_encryption_without_key_fixture():
    with patch(
            "custom_components.candy.config_flow.detect_encryption",
            return_value=(Encryption.ENCRYPTION_WITHOUT_KEY, None)
    ):
        yield


async def test_no_encryption_detected(hass, detect_no_encryption):
    """Test a successful config flow when detected encryption is no encryption."""

    # Initialize a config flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    # Check that the config flow shows the user form as the first step
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_IP_ADDRESS: "192.168.0.66"}
    )

    # Check that the config flow is complete and a new entry is created with
    # the input data
    assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
    assert result["title"] == "Candy"
    assert result["data"] == {
        CONF_IP_ADDRESS: "192.168.0.66",
        CONF_KEY_USE_ENCRYPTION: False,
    }
    assert result["result"]


async def test_detected_encryption_and_key_found(hass, detect_encryption_find_key):
    """Test a successful config flow when encryption is detected and key is found."""

    # Initialize a config flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    # Check that the config flow shows the user form as the first step
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_IP_ADDRESS: "192.168.0.66"}
    )

    # Check that the config flow is complete and a new entry is created with
    # the input data
    assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
    assert result["title"] == "Candy"
    assert result["data"] == {
        CONF_IP_ADDRESS: "192.168.0.66",
        CONF_KEY_USE_ENCRYPTION: True,
        CONF_PASSWORD: "testkey"
    }
    assert result["result"]


async def test_detected_encryption_and_key_not_found(hass, detect_encryption_key_not_found):
    """Test a failing config flow when encryption is detected and key is not found."""
    # Initialize a config flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    # Check that the config flow shows the user form as the first step
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_IP_ADDRESS: "192.168.0.66"}
    )

    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM

    assert result["errors"] == {"base": "detect_encryption"}


async def test_detected_encryption_without_key(hass, detect_encryption_without_key):
    """Test a successful config flow when encryption is detected without using a key."""
    # Initialize a config flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    # Check that the config flow shows the user form as the first step
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_IP_ADDRESS: "192.168.0.66"}
    )

    # Check that the config flow is complete and a new entry is created with
    # the input data
    assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
    assert result["title"] == "Candy"
    assert result["data"] == {
        CONF_IP_ADDRESS: "192.168.0.66",
        CONF_KEY_USE_ENCRYPTION: True,
        CONF_PASSWORD: ""
    }
    assert result["result"]
