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
from fastapi import APIRouter

from aiconsole.core.chat.execution_modes.utils.check_execution_mode_and_get_params import (
    check_execution_mode_and_get_params,
)

router = APIRouter()


@router.get("/params_schema")
async def get_execution_mode_params_schema(module_path: str, notify: bool = True):
    return await check_execution_mode_and_get_params(module_path, notify)
