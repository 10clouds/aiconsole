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

from aiconsole.core.assets.asset import Asset, AssetStatus, AssetType
from aiconsole.core.gpt.consts import GPTMode


class Agent(Asset):
    type: AssetType = AssetType.AGENT
    system: str
    gpt_mode: GPTMode = GPTMode.QUALITY
    execution_mode: str = "aiconsole.core.chat.execution_modes.normal:execution_mode"


class AgentWithStatus(Agent):
    status: AssetStatus = AssetStatus.ENABLED
