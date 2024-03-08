from pydantic import BaseModel

from aiconsole.core.assets.types import Asset


class Root(BaseModel):
    assets: list[Asset]
