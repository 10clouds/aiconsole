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
import datetime
import logging

import watchdog.events
import watchdog.observers

from aiconsole.api.websockets.connection_manager import connection_manager
from aiconsole.api.websockets.server_messages import AssetsUpdatedServerMessage
from aiconsole.core.assets.fs.delete_asset_from_fs import delete_asset_from_fs
from aiconsole.core.assets.fs.move_asset_in_fs import move_asset_in_fs
from aiconsole.core.assets.fs.project_asset_exists_fs import project_asset_exists_fs
from aiconsole.core.assets.fs.save_asset_to_fs import save_asset_to_fs
from aiconsole.core.assets.load_all_assets import load_all_assets
from aiconsole.core.assets.models import Asset, AssetLocation, AssetStatus, AssetType
from aiconsole.core.project import project
from aiconsole.core.project.paths import get_project_assets_directory
from aiconsole.core.settings.settings import settings
from aiconsole.utils.BatchingWatchDogHandler import BatchingWatchDogHandler
from aiconsole_toolkit.settings.partial_settings_data import PartialSettingsData

_log = logging.getLogger(__name__)


class Assets:
    # _assets have lists, where the 1st element is the one overriding the others
    # Currently there can be only 1 overriden element
    _assets: dict[str, list[Asset]]

    def __init__(self, asset_type: AssetType):
        self._suppress_notification_until: datetime.datetime | None = None
        self.asset_type = asset_type
        self._assets = {}

        self.observer = watchdog.observers.Observer()

        get_project_assets_directory(asset_type).mkdir(parents=True, exist_ok=True)
        self.observer.schedule(
            BatchingWatchDogHandler(self.reload),
            get_project_assets_directory(asset_type),
            recursive=True,
        )
        self.observer.start()

    def stop(self):
        self.observer.stop()

    def all_assets(self) -> list[Asset]:
        """
        Return all loaded assets.
        """
        return list(assets[0] for assets in self._assets.values())

    def assets_with_status(self, status: AssetStatus) -> list[Asset]:
        """
        Return all loaded assets with a specific status.
        """
        return [
            assets[0] for assets in self._assets.values() if self.get_status(self.asset_type, assets[0].id) == status
        ]

    async def save_asset(self, asset: Asset, old_asset_id: str, create: bool):
        if asset.defined_in != AssetLocation.PROJECT_DIR and not create:
            raise Exception("Cannot save asset not defined in project.")

        exists_in_project = project_asset_exists_fs(self.asset_type, asset.id)
        old_exists = project_asset_exists_fs(self.asset_type, old_asset_id)

        if create and exists_in_project:
            create = False

        if not create and not exists_in_project:
            raise Exception(f"Asset {asset.id} does not exist.")

        rename = False
        if create and old_asset_id and not exists_in_project and old_exists:
            await move_asset_in_fs(asset.type, old_asset_id, asset.id)
            Assets.rename_asset(asset.type, old_asset_id, asset.id)
            rename = True

        new_asset = await save_asset_to_fs(asset)

        if asset.id not in self._assets:
            self._assets[asset.id] = []

        # integrity checks and deleting old assets from structure
        if not create:
            if not self._assets[asset.id] or self._assets[asset.id][0].defined_in != AssetLocation.PROJECT_DIR:
                raise Exception(f"Asset {asset.id} cannot be edited")
            self._assets[asset.id].pop(0)
        else:
            if self._assets[asset.id] and self._assets[asset.id][0].defined_in == AssetLocation.PROJECT_DIR:
                raise Exception(f"Asset {asset.id} already exists")

        self._assets[asset.id].insert(0, new_asset)

        self._suppress_notification()

        return rename

    async def delete_asset(self, asset_id):
        self._assets[asset_id].pop(0)

        if len(self._assets[asset_id]) == 0:
            del self._assets[asset_id]

        delete_asset_from_fs(self.asset_type, asset_id)

        self._suppress_notification()

    def _suppress_notification(self):
        self._suppress_notification_until = datetime.datetime.now() + datetime.timedelta(seconds=10)

    def get_asset(self, id, location: AssetLocation | None = None):
        """
        Get a specific asset.
        """
        if id not in self._assets or len(self._assets[id]) == 0:
            return None

        for asset in self._assets[id]:
            if location is None or asset.defined_in == location:
                return asset

        return None

    async def reload(self, initial: bool = False):
        _log.info(f"Reloading {self.asset_type}s ...")

        self._assets = await load_all_assets(self.asset_type)

        await connection_manager().send_to_all(
            AssetsUpdatedServerMessage(
                initial=(
                    initial
                    or not (
                        not self._suppress_notification_until
                        or self._suppress_notification_until < datetime.datetime.now()
                    )
                ),
                asset_type=self.asset_type,
                count=len(self._assets),
            )
        )

    @staticmethod
    def get_status(asset_type: AssetType, id: str) -> AssetStatus:
        s = settings().unified_settings

        if asset_type == AssetType.MATERIAL:
            if id in s.materials:
                return s.materials[id]
            asset = project.get_project_materials().get_asset(id)
            default_status = asset.default_status if asset else AssetStatus.ENABLED
            return default_status
        elif asset_type == AssetType.AGENT:
            if id in s.agents:
                return s.agents[id]
            asset = project.get_project_agents().get_asset(id)
            default_status = asset.default_status if asset else AssetStatus.ENABLED
            return default_status

        else:
            raise ValueError(f"Unknown asset type {asset_type}")

    @staticmethod
    def set_status(asset_type: AssetType, id: str, status: AssetStatus, to_global: bool = False) -> None:
        if asset_type == AssetType.MATERIAL:
            settings().save(PartialSettingsData(materials={id: status}), to_global=to_global)
        elif asset_type == AssetType.AGENT:
            settings().save(PartialSettingsData(agents={id: status}), to_global=to_global)
        else:
            raise ValueError(f"Unknown asset type {asset_type}")

    @staticmethod
    def rename_asset(asset_type: AssetType, old_id: str, new_id: str):
        if asset_type == AssetType.MATERIAL:
            partial_settings = PartialSettingsData(
                materials_to_reset=[old_id],
                materials={new_id: Assets.get_status(asset_type, old_id)},
            )
        elif asset_type == AssetType.AGENT:
            partial_settings = PartialSettingsData(
                agents_to_reset=[old_id],
                agents={new_id: Assets.get_status(asset_type, old_id)},
            )
        else:
            raise ValueError(f"Unknown asset type {asset_type}")

        settings().save(partial_settings, to_global=False)
