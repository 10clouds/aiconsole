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

import random

from aiconsole.core.assets.types import AssetType
from aiconsole.core.project import project


def create_materials_str(materials_ids: list | None, ai_can_add_extra_materials: bool) -> str:
    new_line = "\n"

    # We add forced becuase it may influence the choice of enabled materials
    available_materials = []
    if materials_ids:
        for material in project.get_project_assets().cached_assets.values():
            if material[0].id in materials_ids:
                available_materials.append(material[0])

    if ai_can_add_extra_materials:
        available_materials = [
            *available_materials,
            *[
                asset
                for asset in project.get_project_assets().assets_with_enabled_flag_set_to(True)
                if asset.type == AssetType.MATERIAL
            ],
        ]

    random.shuffle(available_materials)

    random_materials = (
        new_line.join([f"* {c.id} - {c.usage}" for c in available_materials]) if available_materials else ""
    )

    return random_materials
