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
import os
import shutil

import rtoml

from aiconsole.core.assets.agents.agent import AICAgent
from aiconsole.core.assets.fs.exceptions import UserIsAnInvalidAgentIdError
from aiconsole.core.assets.fs.load_asset_from_fs import load_asset_from_fs
from aiconsole.core.assets.materials.material import AICMaterial, MaterialContentType
from aiconsole.core.assets.types import Asset
from aiconsole.core.assets.users.users import AICUserProfile
from aiconsole.core.project.paths import (
    get_core_assets_directory,
    get_project_assets_directory,
)

_USER_AGENT_ID = "user"


def only_name_changed(old_asset: Asset | None, asset: Asset):
    if not old_asset:
        return False

    old_asset_dict = old_asset.model_dump()
    asset_dict = asset.model_dump()
    return any(key != "name" and asset_dict.get(key) != old_asset_dict.get(key) for key in asset_dict)


async def save_asset_to_fs(asset: Asset, old_asset_id: str) -> Asset:
    if isinstance(asset, AICAgent):
        if asset.id == _USER_AGENT_ID:
            raise UserIsAnInvalidAgentIdError()

    if asset.id == "new":
        raise ValueError("Cannot save asset with id 'new'")

    project_assets_directory_path = get_project_assets_directory(asset.type)
    project_assets_directory_path.mkdir(parents=True, exist_ok=True)
    file_path = project_assets_directory_path / f"{asset.id}.toml"

    original_st_mtime = None
    if file_path.exists():
        original_st_mtime = os.stat(file_path).st_mtime

    try:
        old_asset = await load_asset_from_fs(asset.type, asset.id)
        current_version = old_asset.version
    except KeyError:
        old_asset = None
        current_version = "0.0.1"

    update_last_modified = not only_name_changed(old_asset, asset)

    current_version_parts = current_version.split(".")

    # Increment version number
    current_version_parts[-1] = str(int(current_version_parts[-1]) + 1)

    # Join version number
    asset.version = ".".join(current_version_parts)

    toml_data = {
        "name": asset.name,
        "version": asset.version,
        "usage": asset.usage,
        "usage_examples": asset.usage_examples,
        "enabled_by_default": asset.enabled_by_default,
    }

    if isinstance(asset, AICMaterial):
        material: AICMaterial = asset
        toml_data["content_type"] = asset.content_type.value
        content_key = {
            MaterialContentType.STATIC_TEXT: "content_static_text",
            MaterialContentType.DYNAMIC_TEXT: "content_dynamic_text",
            MaterialContentType.API: "content_api",
        }[asset.content_type]
        toml_data[content_key] = make_sure_starts_and_ends_with_newline(material.content)

    if isinstance(asset, AICAgent):
        toml_data.update(
            {
                "system": asset.system,
                "gpt_mode": str(asset.gpt_mode),
                "execution_mode": asset.execution_mode,
                "execution_mode_params_values": asset.execution_mode_params_values,
            }
        )

    if isinstance(asset, AICUserProfile):
        toml_data.update(
            {
                "display_name": asset.display_name,
                "profile_picture": asset.profile_picture,
            }
        )

    rtoml.dump(toml_data, file_path)

    if original_st_mtime and not update_last_modified:
        os.utime(file_path, (original_st_mtime, original_st_mtime))

    extensions = [".jpeg", ".jpg", ".png", ".gif", ".SVG"]
    for extension in extensions:
        old_file_path = get_core_assets_directory(asset.type) / f"{old_asset_id}{extension}"
        new_file_path = project_assets_directory_path / f"{asset.id}{extension}"
        if old_file_path.exists():
            shutil.copy(old_file_path, new_file_path)

    return asset


def make_sure_starts_and_ends_with_newline(s: str):
    if not s.startswith("\n"):
        s = "\n" + s

    if not s.endswith("\n"):
        s = s + "\n"

    return s
