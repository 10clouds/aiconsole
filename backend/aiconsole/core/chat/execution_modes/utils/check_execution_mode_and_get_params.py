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

from pydantic import BaseModel

from aiconsole.api.websockets.connection_manager import connection_manager
from aiconsole.api.websockets.server_messages import (
    ErrorServerMessage,
    NotificationServerMessage,
)


async def check_execution_mode_and_get_params(execution_mode_path: str, notify: bool = True):
    split = execution_mode_path.split(":")

    if len(split) != 2:
        await connection_manager().send_to_all(
            ErrorServerMessage(
                error="Invalid execution mode path - should be module_name:object_name",
            )
        )
        return None

    module_name, object_name = split

    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError:
        await connection_manager().send_to_all(
            ErrorServerMessage(
                error=f"Module {module_name} does not exist",
            )
        )
        return None

    obj = getattr(module, object_name, None)

    if obj is None:
        await connection_manager().send_to_all(
            ErrorServerMessage(
                error=f"Could not find {object_name} in {module_name} module",
            )
        )
        return None

    ExecutionModeParams = getattr(module, "ExecutionModeParams", None)

    if ExecutionModeParams is None:
        if notify:
            await connection_manager().send_to_all(
                NotificationServerMessage(
                    title="Execution mode exists",
                    message="Execution mode does not have any parameters",
                )
            )
        return None

    if not issubclass(ExecutionModeParams, BaseModel):
        await connection_manager().send_to_all(
            ErrorServerMessage(
                error="Execution mode parameters definition is not valid",
            )
        )
        return None

    params = ExecutionModeParams.model_json_schema()["properties"]
    param_names = [param["title"] for param in params.values()]

    if notify:
        await connection_manager().send_to_all(
            NotificationServerMessage(
                title="Execution mode exists",
                message=f"Execution mode has parameters: {', '.join(param_names)}",
            )
        )

    return params
