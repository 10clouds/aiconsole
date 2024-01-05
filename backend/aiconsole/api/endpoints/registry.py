from functools import lru_cache

from aiconsole.api.endpoints.services import Agents, Materials


@lru_cache
def agents() -> Agents:
    return Agents()


@lru_cache
def materials() -> Materials:
    return Materials()
