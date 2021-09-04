import aresponses
from pytest_homeassistant_custom_component.common import load_fixture, MockConfigEntry
from homeassistant.const import CONF_IP_ADDRESS, CONF_PASSWORD
from homeassistant.core import HomeAssistant

from custom_components.candy import DOMAIN, CONF_KEY_USE_ENCRYPTION

TEST_IP = "192.168.0.66"
TEST_ENCRYPTION_KEY = ""


def status_response(filename):
    return aresponses.Response(
        text=load_fixture(filename),
        content_type="text/html"  # Shame on Candy, but this is how the real API responds
    )


async def init_integration(hass: HomeAssistant, aioclient_mock, status_response: str):
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="123-456",
        data={
            CONF_IP_ADDRESS: "192.168.0.66",
            CONF_KEY_USE_ENCRYPTION: False,
            CONF_PASSWORD: "asdasdasd",
        }
    )

    aioclient_mock.get(f"http://{TEST_IP}/http-read.json?encrypted=0", text=status_response)

    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
