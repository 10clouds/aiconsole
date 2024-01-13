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

import json
import logging
import os

from fastapi import APIRouter, HTTPException

from aiconsole.consts import COMMANDS_HISTORY_JSON, HISTORY_LIMIT
from aiconsole.core.chat.types import Command
from aiconsole.core.project.paths import get_aic_directory

_log = logging.getLogger(__name__)


router = APIRouter()


def read_command_history() -> list[str]:
    file_path = os.path.join(get_aic_directory(), COMMANDS_HISTORY_JSON)
    try:
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return json.load(f)
        return []
    except IOError as error:
        _log.exception(f"Failed to read the command history file: {file_path}", exc_info=error)
        raise HTTPException(status_code=500, detail=str(error))


def write_command_history(commands: list[str]):
    file_path = os.path.join(get_aic_directory(), COMMANDS_HISTORY_JSON)
    try:
        with open(file_path, "w") as f:
            json.dump(commands, f)
    except IOError as error:
        _log.exception(f"Failed to write the command history file: {file_path}", exc_info=error)
        raise HTTPException(status_code=500, detail=str(error))


@router.get("/commands/history")
def get_history() -> list[str]:
    """Fetches the history of sent commands."""
    return read_command_history()


@router.post("/commands/history")
def save_history(command: Command) -> list[str]:
    """
    Saves the history of sent commands to <commands_history_dir>/<commands_history_json>
    """
    commands = read_command_history()

    commands = [item for item in commands if item.lower() != command.command.lower()]

    commands.append(command.command)
    commands = commands[-HISTORY_LIMIT:]

    write_command_history(commands)
    return commands
