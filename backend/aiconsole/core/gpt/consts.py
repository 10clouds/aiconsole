# The AIConsole Project
#
# Copyright 2023 10Clouds
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from enum import Enum
from typing import Any

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema


class GPTMode(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls, handler(str))


COST_GPT_MODE = GPTMode("cost")
QUALITY_GPT_MODE = GPTMode("quality")
SPEED_GPT_MODE = GPTMode("speed")
ANALYSIS_GPT_MODE = GPTMode("analysis")

GPT_MODE_COST_MODEL = "gpt-3.5-turbo-16k-0613"
GPT_MODE_QUALITY_MODEL = "gpt-4-1106-preview"
GPT_MODE_ANALYSIS_MODEL = "gpt-4-1106-preview"
GPT_MODE_SPEED_MODEL = "gpt-3.5-turbo-16k-0613"

GPT_MODE_COST_MAX_TOKENS = 16384
GPT_MODE_QUALITY_MAX_TOKENS = 128000
GPT_MODE_ANALYSIS_MAX_TOKENS = 128000
GPT_MODE_SPEED_MAX_TOKENS = 16384


class GPTEncoding(str, Enum):
    GPT_4 = "gpt-4"
    GPT_35 = "gpt-3.5-turbo"
