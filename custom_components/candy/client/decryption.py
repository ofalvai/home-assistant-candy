import itertools
import json
import logging
import math
import string
from enum import Enum

from typing import Optional, Iterable

# Adapted from https://www.online-python.com/pm93n5Sqg4

_LOGGER = logging.getLogger(__name__)

KEY_LEN = 16
KEY_CHARSET_CODEPOINTS: list[int] = [ord(c) for c in string.ascii_letters + string.digits]
PLAINTEXT_CHARSET_CODEPOINTS: list[int] = [ord(c) for c in string.printable]


class Encryption(Enum):
    NO_ENCRYPTION = 1  # Use `encrypted=0` in request, response is plaintext JSON
    ENCRYPTION = 2  # Use `encrypted=1` in request, response is encrypted bytes in hex encoding

    # Use `encrypted=1` in request, response is unencrypted hex bytes
    # https://github.com/ofalvai/home-assistant-candy/issues/35#issuecomment-965557116)
    ENCRYPTION_WITHOUT_KEY = 3


def find_key(encrypted_response: bytes) -> Optional[str]:
    candidate_key_codepoints: list[list[int]] = [
        list(_find_candidate_key_codepoints(encrypted_response, i)) for i in range(16)
    ]

    number_of_keys = math.prod(len(l) for l in candidate_key_codepoints)
    _LOGGER.info("%d keys to test", number_of_keys)

    for key in itertools.product(*candidate_key_codepoints):
        decrypted = decrypt(key, encrypted_response)
        if _is_valid_json(decrypted):
            key_str = "".join(chr(point) for point in key)
            _LOGGER.info("Potential key found: %s", key_str)
            return key_str

    return None


def decrypt(key: bytes, encrypted_response: bytes) -> bytes:
    key_len = len(key)
    decrypted: list[int] = []
    for (i, byte) in enumerate(encrypted_response):
        decrypted.append(byte ^ key[i % key_len])
    return bytes(decrypted)


def _find_candidate_key_codepoints(encrypted_response: bytes, key_offset: int) -> Iterable[int]:
    bytes_to_check: bytes = encrypted_response[key_offset::KEY_LEN]
    for point in KEY_CHARSET_CODEPOINTS:
        if all(point ^ byte in PLAINTEXT_CHARSET_CODEPOINTS for byte in bytes_to_check):
            yield point


def _is_valid_json(decrypted: bytes) -> bool:
    try:
        json.loads(decrypted)
    except json.JSONDecodeError:
        return False
    return True
