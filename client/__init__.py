import codecs
import json
import logging

import aiohttp
import backoff
from aiohttp import ClientSession

from .model import MachineStatus

_LOGGER = logging.getLogger(__name__)


class CandyClient:

    def __init__(self, session: ClientSession, device_ip: str, encryption_key: str):
        self.session = session  # Session is the default HA session, shouldn't be cleaned up
        self.device_ip = device_ip
        self.encryption_key = encryption_key

    @backoff.on_exception(backoff.expo, aiohttp.ClientError, max_tries=10)
    @backoff.on_exception(backoff.expo, TimeoutError, max_tries=10)
    async def status(self) -> MachineStatus:
        url = f"http://{self.device_ip}/http-read.json?encrypted=1"
        async with self.session.get(url) as resp:
            resp_bytes = await resp.read()
            resp_hex = codecs.decode(resp_bytes, encoding="hex")
            decrypted_text = self.decrypt(resp_hex, self.encryption_key)

            resp_json = json.loads(decrypted_text)
            _LOGGER.debug(resp_json)
            status = MachineStatus.from_json(resp_json["statusLavatrice"])
            return status

    def decrypt(self, cipher_text, key):
        decrypted = ""
        for i in range(len(cipher_text)):
            decrypted += chr(cipher_text[i] ^ ord(key[i % len(key)]))

        return decrypted
