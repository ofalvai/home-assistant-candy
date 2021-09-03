import aresponses
from pytest_homeassistant_custom_component.common import load_fixture

TEST_IP = "192.168.0.66"
TEST_ENCRYPTION_KEY = ""


def status_response(filename):
    return aresponses.Response(
        text=load_fixture(filename),
        content_type="text/html"  # Shame on Candy, but this is how the real API responds
    )
