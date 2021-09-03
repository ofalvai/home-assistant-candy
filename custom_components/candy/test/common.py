import os

import aresponses

TEST_IP = "192.168.0.66"
TEST_ENCRYPTION_KEY = ""


def load_fixture(filename):
    path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
    with open(path, encoding="utf-8") as fptr:
        return fptr.read()


def status_response(filename):
    return aresponses.Response(
        text=load_fixture(filename),
        content_type="text/html"  # Shame on Candy, but this is how the real API responds
    )
