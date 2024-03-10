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
from collections import defaultdict

import watchdog.events
import watchdog.observers

from aiconsole.api.websockets.connection_manager import connection_manager
from aiconsole.api.websockets.server_messages import AssetsUpdatedServerMessage
from aiconsole.core.assets.fs.delete_asset_from_fs import delete_asset_from_fs
from aiconsole.core.assets.fs.move_asset_in_fs import move_asset_in_fs
from aiconsole.core.assets.fs.project_asset_exists_fs import project_asset_exists_fs
from aiconsole.core.assets.fs.save_asset_to_fs import save_asset_to_fs
from aiconsole.core.assets.materials.material import AICMaterial, MaterialContentType
from aiconsole.core.assets.types import Asset, AssetLocation, AssetType
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

    def __init__(self):
        self._suppress_notification_until: datetime.datetime | None = None
        self._assets = {}

        self.observer = watchdog.observers.Observer()

        for asset_type in [AssetType.AGENT, AssetType.MATERIAL, AssetType.CHAT]:
            get_project_assets_directory(asset_type).mkdir(parents=True, exist_ok=True)

        self.observer.schedule(
            BatchingWatchDogHandler(self.reload),
            ".",  # get_project_assets_directory(asset_type),
            recursive=True,
        )
        self.observer.start()

    def stop(self):
        self.observer.stop()

    def all_assets(self) -> list[Asset]:
        """
        Return all loaded assets.
        """
        return list(assets[0] for assets in self._assets.values() if assets)

    def assets_with_enabled_flag_set_to(self, enabled: bool) -> list[Asset]:
        """
        Return all loaded assets with a specific status.
        """
        return [assets[0] for assets in self._assets.values() if self.is_enabled(assets[0].id) == enabled]

    async def save_asset(self, asset: Asset, old_asset_id: str, create: bool):
        if asset.defined_in != AssetLocation.PROJECT_DIR and not create:
            raise Exception("Cannot save asset not defined in project.")

        exists_in_project = project_asset_exists_fs(asset.type, asset.id)
        old_exists = project_asset_exists_fs(asset.type, old_asset_id)

        if create and exists_in_project:
            create = False

        if not create and not exists_in_project:
            raise Exception(f"Asset {asset.id} does not exist.")

        rename = False
        if create and old_asset_id and not exists_in_project and old_exists:
            await move_asset_in_fs(asset.type, old_asset_id, asset.id)
            Assets.rename_asset(asset.type, old_asset_id, asset.id)
            rename = True

        if isinstance(asset, AICMaterial):
            if asset.content_type in (MaterialContentType.DYNAMIC_TEXT, MaterialContentType.API):
                if not asset.content.startswith("file://"):
                    file_path = await AICMaterial.save_content_to_file(asset.id, asset.content)
                    asset.content = f"file://{file_path}"

        new_asset = await save_asset_to_fs(asset, old_asset_id)

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
        asset = self._assets[asset_id].pop(0)

        if len(self._assets[asset_id]) == 0:
            del self._assets[asset_id]

        delete_asset_from_fs(asset.type, asset_id)

        self._suppress_notification()

    def _suppress_notification(self):
        self._suppress_notification_until = datetime.datetime.now() + datetime.timedelta(seconds=10)

    def get_asset(
        self, id, location: AssetLocation | None = None, type: AssetType | None = None, enabled: bool | None = None
    ):
        """
        Get a specific asset.
        """
        if id not in self._assets or len(self._assets[id]) == 0:
            return None

        for asset in self._assets[id]:
            if location is None or asset.defined_in == location:
                if type and asset.type != type:
                    return None

                if enabled is not None and self.is_enabled(asset.id) != enabled:
                    return None

                return asset

        return None

    async def reload(self, initial: bool = False):
        from aiconsole.core.assets.load_all_assets import load_all_assets

        _log.info("Reloading assets ...")

        li: dict[str, list[Asset]] = defaultdict(list)
        for asset_type in [AssetType.AGENT, AssetType.MATERIAL, AssetType.CHAT, AssetType.USER]:
            d = await load_all_assets(asset_type)

            # This might not be bulletproof, what if the settings are loaded after the assets? the backend should not use .enabled directly ...
            # How to properly mix dynamic data or even per user data (chat options) with static data (assets, chats etc.)?
            for k, v in d.items():
                for asset in v:
                    asset.enabled = self.is_enabled(asset.id)

            for k, v in d.items():
                li[k].extend(v)
        self._assets = li

        await connection_manager().send_to_all(
            AssetsUpdatedServerMessage(
                initial=(
                    initial
                    or not (
                        not self._suppress_notification_until
                        or self._suppress_notification_until < datetime.datetime.now()
                    )
                ),
                count=len(self._assets),
            )
        )

    @staticmethod
    def is_enabled(id: str) -> bool:
        s = settings().unified_settings

        if id in s.assets:
            return s.assets[id]

        asset = project.get_project_assets().get_asset(id)
        default_status = asset.enabled_by_default if asset else True
        return default_status

    @staticmethod
    def set_enabled(id: str, enabled: bool, to_global: bool = False) -> None:
        settings().save(PartialSettingsData(assets={id: enabled}), to_global=to_global)

    @staticmethod
    def rename_asset(asset_type: AssetType, old_id: str, new_id: str):
        partial_settings = PartialSettingsData(
            assets_to_reset=[old_id],
            assets={new_id: Assets.is_enabled(old_id)},
        )

        settings().save(partial_settings, to_global=False)
