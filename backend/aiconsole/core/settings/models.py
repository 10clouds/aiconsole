from typing import Optional

from pydantic import BaseModel

from aiconsole.core.assets.models import AssetStatus
from aiconsole.core.users.models import UserProfile


class PartialSettingsData(BaseModel):
    code_autorun: Optional[bool] = None
    openai_api_key: Optional[str] = None
    user_profile_settings: Optional[UserProfile] = None
    materials: Optional[dict[str, AssetStatus]] = None
    materials_to_reset: Optional[list[str]] = None
    agents: Optional[dict[str, AssetStatus]] = None
    agents_to_reset: Optional[list[str]] = None
    to_global: bool = False


class SettingsData(BaseModel):
    code_autorun: bool = False
    openai_api_key: str | None = None
    user_profile: UserProfile | None = None
    materials: dict[str, AssetStatus] = {}
    agents: dict[str, AssetStatus] = {}
