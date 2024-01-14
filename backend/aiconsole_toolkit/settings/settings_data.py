from typing import Any

from pydantic import BaseModel, model_validator

from aiconsole.core.assets.models import AssetStatus
from aiconsole.core.gpt import consts
from aiconsole.core.gpt.types import GPTModeConfig
from aiconsole.core.users.models import UserProfile


class SettingsData(BaseModel):
    code_autorun: bool = False
    openai_api_key: str | None = None
    user_profile: UserProfile = UserProfile()
    materials: dict[str, AssetStatus] = {}
    agents: dict[str, AssetStatus] = {}
    gpt_modes: dict[str, GPTModeConfig] = {
        "speed": GPTModeConfig(
            max_tokens=consts.GPT_MODE_SPEED_MAX_TOKENS,
            encoding=consts.GPTEncoding.GPT_4,
            model=consts.GPT_MODE_SPEED_MODEL,
            api_key="openai_api_key",
        ),
        "quality": GPTModeConfig(
            max_tokens=consts.GPT_MODE_QUALITY_MAX_TOKENS,
            encoding=consts.GPTEncoding.GPT_4,
            model=consts.GPT_MODE_QUALITY_MODEL,
            api_key="openai_api_key",
        ),
        "cost": GPTModeConfig(
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
