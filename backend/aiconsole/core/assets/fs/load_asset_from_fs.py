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
import logging
import os
import pathlib
from datetime import datetime

import aiofiles
import aiofiles.os as async_os
import rtoml

from aiconsole.core.assets.agents.agent import AICAgent
from aiconsole.core.assets.fs.exceptions import UserIsAnInvalidAgentIdError
from aiconsole.core.assets.materials.material import AICMaterial, MaterialContentType
from aiconsole.core.assets.types import Asset, AssetLocation, AssetType
from aiconsole.core.assets.users.users import AICUserProfile
from aiconsole.core.gpt.consts import GPTMode
from aiconsole.core.project.paths import (
    get_core_assets_directory,
    get_project_assets_directory,
)
from aiconsole.core.users.types import UserProfile

_log = logging.getLogger(__name__)


_USER_AGENT_ID = "user"

# LEGACY: Port 2.9 agent to 2.11
execution_mode_path_mapping = {
    "aiconsole.core.execution_modes.normal:execution_mode_normal": "aiconsole.core.chat.execution_modes.normal:execution_mode",
    "aiconsole.core.execution_modes.interpreter:execution_mode_interpreter": "aiconsole.core.chat.execution_modes.interpreter:execution_mode",
    "aiconsole.core.execution_modes.example_countdown:execution_mode_example_countdown": "aiconsole.core.chat.execution_modes.example_countdown:execution_mode",
}


async def _find_asset_path(
    asset_type: AssetType, asset_id: str, location: AssetLocation | None
) -> tuple[AssetLocation, pathlib.Path]:
    project_dir_path = get_project_assets_directory(asset_type)
    core_resource_path = get_core_assets_directory(asset_type)
    asset_filename = f"{asset_id}.toml"

    project_asset_path = project_dir_path / asset_filename
    core_asset_path = core_resource_path / asset_filename

    if project_asset_path.exists() and (location is None or location == AssetLocation.PROJECT_DIR):
        return AssetLocation.PROJECT_DIR, project_asset_path
    elif core_asset_path.exists() and (location is None or location == AssetLocation.AICONSOLE_CORE):
        return AssetLocation.AICONSOLE_CORE, core_asset_path
    else:
        raise KeyError(f"Asset {asset_id} not found")


async def load_asset_from_fs(asset_type: AssetType, asset_id: str, location: AssetLocation | None = None) -> Asset:
    if asset_type == AssetType.AGENT and asset_id == _USER_AGENT_ID:
        raise UserIsAnInvalidAgentIdError()

    location, path = await _find_asset_path(asset_type, asset_id, location)

    async with aiofiles.open(path, mode="r", encoding="utf8", errors="replace") as file:
        content = await file.read()
        tomldoc = rtoml.loads(content)

    asset_id = os.path.splitext(os.path.basename(path))[0]
    stat = await async_os.stat(path)

    params = {
        "id": asset_id,
        "name": str(tomldoc.get("name", asset_id)).strip(),
        "version": str(tomldoc.get("version", "0.0.1")).strip(),
        "defined_in": location,
        "usage": str(tomldoc["usage"]).strip(),
        "usage_examples": tomldoc.get("usage_examples", []),
        "enabled_by_default": tomldoc.get(
            "enabled_by_default", str(tomldoc.get("default_status", "enabled")).strip() == "enabled"
        ),
        "override": location == AssetLocation.PROJECT_DIR
        and (get_core_assets_directory(asset_type) / f"{asset_id}.toml").exists(),
        "last_modified": datetime.fromtimestamp(stat.st_mtime),
    }

    if asset_type == AssetType.MATERIAL:
        material = AICMaterial(
            **params,
            content_type=MaterialContentType(str(tomldoc["content_type"]).strip()),
        )

        if "content" in tomldoc:
            material.content = str(tomldoc["content"]).strip()

        if "content_static_text" in tomldoc and material.content_type == MaterialContentType.STATIC_TEXT:
            material.content = str(tomldoc["content_static_text"]).strip()

        if "content_dynamic_text" in tomldoc and material.content_type == MaterialContentType.DYNAMIC_TEXT:
            material.content = str(tomldoc["content_dynamic_text"]).strip()

        if "content_api" in tomldoc and material.content_type == MaterialContentType.API:
            material.content = str(tomldoc["content_api"]).strip()

        return material

    if asset_type == AssetType.AGENT:
        params["system"] = str(tomldoc["system"]).strip()

        params["gpt_mode"] = GPTMode(tomldoc.get("gpt_mode", "").strip())

        execution_mode = tomldoc.get("execution_mode", "")

        params["execution_mode"] = execution_mode_path_mapping.get(execution_mode, execution_mode)

        params["execution_mode_params_values"] = tomldoc.get("execution_mode_params_values", {})

        return AICAgent(**params)

    if asset_type == AssetType.USER:
        userProfile = UserProfile(id=params["id"], **tomldoc)
        params.update(userProfile.model_dump())
        user = AICUserProfile(**params)

        return user

    raise Exception(f"Asset type {asset_type} not supported.")
