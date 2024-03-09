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

from datetime import datetime
from enum import Enum

from pydantic import field_serializer

from fastmutation.types import BaseObject


class AssetLocation(str, Enum):
    AICONSOLE_CORE = "aiconsole"
    PROJECT_DIR = "project"


class AssetType(str, Enum):
    AGENT = "agent"
    MATERIAL = "material"
    CHAT = "chat"
    USER = "user"


class Asset(BaseObject):
    name: str
    version: str = "0.0.1"
    usage: str
    usage_examples: list[str]
    defined_in: AssetLocation
    type: AssetType
    enabled_by_default: bool = True
    enabled: bool = True
    override: bool
    last_modified: datetime

    @field_serializer("last_modified")
    def serialize_dt(self, dt: datetime, _info):
        return dt.isoformat()
