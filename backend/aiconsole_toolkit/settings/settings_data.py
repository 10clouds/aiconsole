from typing import Any

from pydantic import BaseModel, model_validator

from aiconsole.core.assets.models import AssetStatus
from aiconsole.core.gpt import consts
from aiconsole.core.gpt.types import GPTModeConfig
from aiconsole.core.users.models import UserProfile

REFERENCE_TO_GLOBAL_OPENAI_KEY = "ref/openai_api_key"


class SettingsData(BaseModel):
    code_autorun: bool = False
    openai_api_key: str | None = None
    user_profile: UserProfile = UserProfile()
    materials: dict[str, AssetStatus] = {}
    agents: dict[str, AssetStatus] = {}
    gpt_modes: dict[consts.GPTMode, GPTModeConfig] = {
        consts.ANALYSIS_GPT_MODE: GPTModeConfig(
            max_tokens=consts.GPT_MODE_ANALYSIS_MAX_TOKENS,
            encoding=consts.GPTEncoding.GPT_4,
            model=consts.GPT_MODE_ANALYSIS_MODEL,
            api_key=REFERENCE_TO_GLOBAL_OPENAI_KEY,
        ),
        consts.SPEED_GPT_MODE: GPTModeConfig(
            max_tokens=consts.GPT_MODE_SPEED_MAX_TOKENS,
            encoding=consts.GPTEncoding.GPT_4,
            model=consts.GPT_MODE_SPEED_MODEL,
            api_key=REFERENCE_TO_GLOBAL_OPENAI_KEY,
        ),
        consts.QUALITY_GPT_MODE: GPTModeConfig(
            max_tokens=consts.GPT_MODE_QUALITY_MAX_TOKENS,
            encoding=consts.GPTEncoding.GPT_4,
            model=consts.GPT_MODE_QUALITY_MODEL,
            api_key=REFERENCE_TO_GLOBAL_OPENAI_KEY,
        ),
        consts.SPEED_GPT_MODE: GPTModeConfig(
            max_tokens=consts.GPT_MODE_COST_MAX_TOKENS,
            encoding=consts.GPTEncoding.GPT_4,
            model=consts.GPT_MODE_COST_MODEL,
            api_key=REFERENCE_TO_GLOBAL_OPENAI_KEY,
        ),
    }
    extra: dict[str, Any] = {}
