import hashlib
import logging
from functools import lru_cache

import requests

from aiconsole.core.clients.models.gravatar import GravatarUserProfile

_log = logging.getLogger(__name__)


class GravatarClient:
    def __init__(self):
        self.base_url = "https://www.gravatar.com"

    def get_profile(self, email: str) -> GravatarUserProfile | None:
        gravatar_url = f"{self.base_url}/{hashlib.md5(email.lower().encode()).hexdigest()}.json"
        try:
            response = requests.get(gravatar_url)
            response.raise_for_status()
            gravatar_data = response.json()
            entry = gravatar_data["entry"][0]
            return GravatarUserProfile(**entry)
        except requests.RequestException as e:
            _log.exception(f"[{self.__class__.__name__}] Request to {gravatar_url} failed.")
            return None


@lru_cache
def gravatar_client() -> GravatarClient:
    return GravatarClient()
