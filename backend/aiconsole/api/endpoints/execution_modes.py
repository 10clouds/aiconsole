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
import importlib
import logging

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

_log = logging.getLogger(__name__)


def read_execution_mode_params_schema(module_path: str):
    if len(module_path.split(":")) != 2:
        _log.error("Invalid module path format. Expected: 'module_name:object_name'")

    module_name = module_path.split(":")[0]

    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError:
        _log.error(f"Module {module_name} not found")
        return None

    ExecutionModeParams = getattr(module, "ExecutionModeParams", None)

    if ExecutionModeParams is None:
        _log.info(f"Module {module_name} does not have a ExecutionModeParams structure")
        return None

    if not issubclass(ExecutionModeParams, BaseModel):
        _log.error(f"ExecutionModeParams in module {module_name} is not a subclass of BaseModel")
        return None

    return ExecutionModeParams.model_json_schema()["properties"]


@router.get("/params_schema")
async def get_execution_mode_params_schema(module_path: str):
    return read_execution_mode_params_schema(module_path)
