from typing import Any, Optional

from pydantic import BaseModel, model_validator

from aiconsole.core.assets.models import AssetStatus
from aiconsole.core.gpt import consts
from aiconsole.core.gpt.types import GPTModeConfig
from aiconsole.core.users.models import PartialUserProfile, UserProfile


class PartialSettingsData(BaseModel):
    code_autorun: Optional[bool] = None
    openai_api_key: Optional[str] = None
    user_profile: Optional[PartialUserProfile] = None
    materials: Optional[dict[str, AssetStatus]] = None
    materials_to_reset: Optional[list[str]] = None
    agents: Optional[dict[str, AssetStatus]] = None
    agents_to_reset: Optional[list[str]] = None
    gpt_modes: Optional[dict[str, GPTModeConfig]] = None
    extra: Optional[dict[str, Any]] = None
    to_global: bool = False


class SettingsData(BaseModel):
    code_autorun: bool = False
    openai_api_key: str | None = None
    user_profile: UserProfile = UserProfile()
    materials: dict[str, AssetStatus] = {}
    agents: dict[str, AssetStatus] = {}
    gpt_modes: dict[str, GPTModeConfig] = {
        "speed": GPTModeConfig(
            name="speed",
            max_tokens=consts.GPT_MODE_SPEED_MAX_TOKENS,
            encoding=consts.GPTEncoding.GPT_4,
            model=consts.GPT_MODE_SPEED_MODEL,
            api_key="openai_api_key",
        ),
        "quality": GPTModeConfig(
            name="quality",
            max_tokens=consts.GPT_MODE_QUALITY_MAX_TOKENS,
            encoding=consts.GPTEncoding.GPT_4,
            model=consts.GPT_MODE_QUALITY_MODEL,
            api_key="openai_api_key",
        ),
        "cost": GPTModeConfig(
            name="cost",
            max_tokens=consts.GPT_MODE_COST_MAX_TOKENS,
            encoding=consts.GPTEncoding.GPT_4,
            model=consts.GPT_MODE_COST_MODEL,
            api_key="openai_api_key",
        ),
    }
    extra: dict[str, Any] = {}

    @model_validator(mode="after")
    def set_openai_keys(self):
        for mode, config in self.gpt_modes.items():
            config.api_key = self.openai_api_key
        return self
