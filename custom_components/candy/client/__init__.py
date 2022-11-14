import json
import logging
from json import JSONDecodeError
from typing import Optional, Tuple, Union

import aiohttp
import backoff
from aiohttp import ClientSession

from aiolimiter import AsyncLimiter

from .decryption import decrypt, Encryption, find_key
from .model import (DishwasherStatus, OvenStatus, TumbleDryerStatus,
                    WashingMachineStatus)

_LOGGER = logging.getLogger(__name__)

# Some devices reportedly can't handle too frequent requests and respond with BAD_REQUEST
# This global limiter makes sure we don't call the API too fast
# https://github.com/ofalvai/home-assistant-candy/issues/61
_LIMITER = AsyncLimiter(max_rate=1, time_period=3)


class CandyClient:

    def __init__(self, session: ClientSession, device_ip: str, encryption_key: str, use_encryption: bool):
        self.session = session  # Session is the default HA session, shouldn't be cleaned up
        self.device_ip = device_ip
        self.encryption_key = encryption_key
        self.use_encryption = use_encryption

    @backoff.on_exception(backoff.expo, aiohttp.ClientError, max_tries=10, logger=__name__)
    @backoff.on_exception(backoff.expo, TimeoutError, max_tries=10, logger=__name__)
    async def status_with_retry(self) -> Union[WashingMachineStatus, TumbleDryerStatus, DishwasherStatus, OvenStatus]:
        return await self.status()

    async def status(self) -> Union[WashingMachineStatus, TumbleDryerStatus, DishwasherStatus, OvenStatus]:
        url = _status_url(self.device_ip, self.use_encryption)
        async with _LIMITER, self.session.get(url) as resp:
            if self.use_encryption:
                resp_hex = await resp.text()  # Response is hex encoded, either encrypted or not
                if self.encryption_key != "":
                    decrypted_text = decrypt(self.encryption_key.encode(), bytes.fromhex(resp_hex))
                else:
                    # Response is just hex encoded without encryption (details in detect_encryption())
                    decrypted_text = bytes.fromhex(resp_hex)
                resp_json = json.loads(decrypted_text)
            else:
                resp_json = await resp.json(content_type="text/html")

            _LOGGER.debug(resp_json)

            if "statusTD" in resp_json:
                status = TumbleDryerStatus.from_json(resp_json["statusTD"])
            elif "statusLavatrice" in resp_json:
                status = WashingMachineStatus.from_json(resp_json["statusLavatrice"])
            elif "statusForno" in resp_json:
                status = OvenStatus.from_json(resp_json["statusForno"])
            elif "statusDWash" in resp_json:
                status = DishwasherStatus.from_json(resp_json["statusDWash"])
            else:
                raise Exception("Unable to detect machine type from API response", resp_json)

            return status


async def detect_encryption(session: aiohttp.ClientSession, device_ip: str) -> Tuple[Encryption, Optional[str]]:
    # noinspection PyBroadException
    try:
        _LOGGER.info("Trying to get a response without encryption (encrypted=0)...")
        url = _status_url(device_ip, use_encryption=False)
        async with _LIMITER, session.get(url) as resp:
            resp_json = await resp.json(content_type="text/html")
            assert resp_json.get("response") != "BAD REQUEST"
            _LOGGER.info("Received unencrypted JSON response, no need to use key for decryption")
            return Encryption.NO_ENCRYPTION, None
    except Exception as err: # pylint: disable=broad-except
        _LOGGER.debug(err)
        _LOGGER.info("Failed to get a valid response without encryption, let's try with encrypted=1...")
        url = _status_url(device_ip, use_encryption=True)
        async with _LIMITER, session.get(url) as resp:
            resp_hex = await resp.text()  # Response is hex encoded encrypted data
            try:
                json.loads(bytes.fromhex(resp_hex))
                _LOGGER.info("Response is not encrypted (despite encryption=1 in request), no need to brute force "
                             "the key")
                return Encryption.ENCRYPTION_WITHOUT_KEY, None
            except JSONDecodeError as json_err:
                _LOGGER.info("Brute force decryption key from the encrypted response...")
                _LOGGER.debug("Response: %s", resp_hex)
                key = find_key(bytes.fromhex(resp_hex))
                if key is None:
                    raise ValueError("Couldn't brute force key") from json_err

                _LOGGER.info("Using key with encrypted=1 for future requests")
                return Encryption.ENCRYPTION, key


def _status_url(device_ip: str, use_encryption: bool) -> str:
    return f"http://{device_ip}/http-read.json?encrypted={1 if use_encryption else 0}"
