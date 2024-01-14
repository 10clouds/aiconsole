from pydantic import BaseModel

from aiconsole.core.assets.models import AssetStatus


class StatusChangePostBody(BaseModel):
    status: AssetStatus
    to_global: bool
