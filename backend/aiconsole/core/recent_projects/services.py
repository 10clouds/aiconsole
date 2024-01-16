import os
from dataclasses import dataclass
from pathlib import Path

import rtoml

from aiconsole.core.assets.materials.material import MaterialContentType
from aiconsole.core.assets.models import AssetType
from aiconsole.core.project.paths import get_core_assets_directory
from aiconsole.utils.list_files_in_file_system import list_files_in_file_system
from aiconsole.utils.resource_to_path import resource_to_path


@dataclass(frozen=True, slots=True)
class MaterialsCounts:
    note: int
    dynamic_note: int
    python_api: int


@dataclass(frozen=True, slots=True)
class AgentsCount:
    count: int
    agent_ids: list[str]


class RecentProjectsStats:
    def get_materials_counts(self, dir: Path) -> MaterialsCounts:
        base_path = dir / "materials"
        core_path = get_core_assets_directory(AssetType.MATERIAL)

        base_ids = (base_path, self._get_asset_ids_in_path(base_path))
        core_ids = (core_path, self._get_asset_ids_in_path(core_path))

        notes_count = 0
        dynamic_notes_count = 0
        python_api_count = 0
        for path, ids in [base_ids, core_ids]:
            for id in ids:
                with open(path / f"{id}.toml", "r") as file:
                    tomldoc = rtoml.loads(file.read())

                content_type = MaterialContentType(str(tomldoc["content_type"]).strip())

                if content_type == MaterialContentType.STATIC_TEXT:
                    notes_count += 1
                elif content_type == MaterialContentType.DYNAMIC_TEXT:
                    dynamic_notes_count += 1
                elif content_type == MaterialContentType.API:
                    python_api_count += 1

        return MaterialsCounts(
            note=notes_count,
            dynamic_note=dynamic_notes_count,
            python_api=python_api_count,
        )

    def get_agents_count(self, dir: Path) -> AgentsCount:
        base_path = dir / "agents"
        core_path = get_core_assets_directory(AssetType.AGENT)

        base_ids = self._get_asset_ids_in_path(base_path)
        core_ids = self._get_asset_ids_in_path(core_path)

        ids = {*base_ids, *core_ids}

        return AgentsCount(count=len(ids), agent_ids=list(ids))

    def _get_asset_ids_in_path(self, dir: Path) -> set[str]:
        return set(
            os.path.splitext(os.path.basename(path))[0]
            for path in list_files_in_file_system(dir)
            if os.path.splitext(Path(path))[-1] == ".toml"
        )
