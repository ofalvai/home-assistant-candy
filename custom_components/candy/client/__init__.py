import codecs
import json
import logging
from typing import Union

import aiohttp
import backoff
from aiohttp import ClientSession

from .model import WashingMachineStatus, TumbleDryerStatus, OvenStatus

_LOGGER = logging.getLogger(__name__)


class CandyClient:

    def __init__(self, session: ClientSession, device_ip: str, encryption_key: str, use_encryption: bool):
        self.session = session  # Session is the default HA session, shouldn't be cleaned up
        self.device_ip = device_ip
        self.encryption_key = encryption_key
        self.use_encryption = use_encryption

    @backoff.on_exception(backoff.expo, aiohttp.ClientError, max_tries=10)
    @backoff.on_exception(backoff.expo, TimeoutError, max_tries=10)
    async def status_with_retry(self) -> Union[WashingMachineStatus, TumbleDryerStatus]:
        return await self.status()

    async def status(self) -> Union[WashingMachineStatus, TumbleDryerStatus]:
        url = f"http://{self.device_ip}/http-read.json?encrypted={1 if self.use_encryption else 0}"
        async with self.session.get(url) as resp:
            if self.use_encryption:
                resp_bytes = await resp.read()
                resp_hex = codecs.decode(resp_bytes, encoding="hex")
                decrypted_text = self.decrypt(resp_hex, self.encryption_key)
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
            else:
                raise Exception("Unable to detect machine type from API response", resp_json)

            return status

    def decrypt(self, cipher_text, key):
        decrypted = ""
        for i in range(len(cipher_text)):
            decrypted += chr(cipher_text[i] ^ ord(key[i % len(key)]))

        return decrypted
