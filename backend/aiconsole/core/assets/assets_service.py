import logging
from dataclasses import dataclass
from functools import lru_cache

from aiconsole.api.websockets.server_messages import AssetsUpdatedServerMessage
from aiconsole.core.assets.assets_storage import AssetsStorage
from aiconsole.core.assets.types import Asset, AssetLocation, AssetType
from aiconsole.core.settings.settings import settings
from aiconsole.utils.events import InternalEvent, internal_events
from aiconsole.utils.notifications import Notifications
from aiconsole_toolkit.settings.partial_settings_data import PartialSettingsData

_log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class AssetsUpdatedEvent(InternalEvent):
    pass


class AssetsAlreadyConfiguredError(Exception):
    pass


class AssetsCleanUpBeforeConfigurationError(Exception):
    pass


class Assets:
    _storage: AssetsStorage | None = None
    _notifications: Notifications | None = None

    async def configure(self, storage: AssetsStorage) -> None:
        """
        Configures the assets storage and notifications.

        :param storage: The assets storage instance to use.
        :raises AssetsAlreadyConfiguredError: If the assets service is already configured and an attempt is made to configure it again without first calling `clean_up`.
        """
        if self.is_configured:
            raise AssetsAlreadyConfiguredError(
                "Assets service is already configure, if want to reconfigure call `clean_up` and configure again."
            )

        await storage.setup()
        self._storage = storage
        self._notifications = Notifications()

        internal_events().subscribe(
            AssetsUpdatedEvent,
            self._when_reloaded,
        )

        _log.info("Settings configured")

    @property
    def unified_assets(self) -> dict[str, list[Asset]]:
        """
        Retrieves all assets from configured sources.

        :return: A dict of unified assets.
        """
        if not self._storage or not self._notifications:
            _log.error("Assets not configured.")
            raise ValueError("Assets not configured")

        return self._storage.assets

    def filter_unified_assets(
        self, location: AssetLocation | None = None, enabled: bool | None = None, asset_type: AssetType | None = None
    ):
        """
        Returns filtered unified_assets.

        :param location: Optional filter by asset location.
        :param enabled: Optional filter by asset enabled status.
        :return: A dict of filtered unified assets.
        """
        all_assets = self.unified_assets

        if location is None and enabled is None:
            return all_assets

        filtered_assets: dict[str, list[Asset]] = {}
        for asset_id, assets in all_assets.items():
            filtered_list = []
            for asset in assets:
                if location is not None and asset.defined_in != location:
                    continue
                if enabled is not None and self.is_asset_enabled(asset.id) != enabled:
                    continue
                if asset_type is not None and asset_type != asset.type:
                    continue
                filtered_list.append(asset)
            if filtered_list:
                filtered_assets[asset_id] = filtered_list

        return filtered_assets

    def clean_up(self) -> None:
        """
        Cleans up resources used by the assets, such as storage and notifications.
        """
        if not self.is_configured:
            raise AssetsCleanUpBeforeConfigurationError

        self._storage.destroy()  # type: ignore

        self._storage = None
        self._notifications = None

        internal_events().unsubscribe(
            AssetsUpdatedEvent,
            self._when_reloaded,
        )

    async def _when_reloaded(self, AssetsUpdatedEvent) -> None:
        """
        Handles the assets updated event asynchronously.

        :param AssetsUpdatedEvent: The event indicating that assets have been updated.
        """
        if not self._storage or not self._notifications:
            _log.error("Assets not configured.")
            raise ValueError("Assets not configured")

        await self._notifications.notify(
            AssetsUpdatedServerMessage(
                initial=self._notifications.to_suppress,
                count=len(self.unified_assets),
            )
        )

    def get_asset(self, asset_id, location: AssetLocation | None = None, enabled: bool | None = None) -> Asset | None:
        if not self._storage or not self._notifications:
            _log.error("Assets not configured.")
            raise ValueError("Assets not configured")

        if asset_id not in self.unified_assets or (
            asset_id in self.unified_assets and len(self.unified_assets[asset_id]) == 0
        ):
            return None

        for asset in self.unified_assets[asset_id]:
            if location is None or asset.defined_in == location:
                if enabled is not None and self.is_asset_enabled(asset.id) != enabled:
                    return None
                return asset

        return None

    # TODO: Why do we need to suppress for all or maybe supress to a specific connection
    async def create_asset(self, asset: Asset) -> None:
        if not self._storage or not self._notifications:
            _log.error("Assets not configured.")
            raise ValueError("Assets not configured")

        self._notifications.suppress_next_notification()
        await self._storage.create_asset(asset)

    async def update_asset(self, original_asset_id: str, updated_asset: Asset, scope: str | None = None):
        if not self._storage or not self._notifications:
            _log.error("Assets not configured.")
            raise ValueError("Assets not configured")

        self._notifications.suppress_next_notification()
        await self._storage.update_asset(original_asset_id, updated_asset, scope)

        if original_asset_id != updated_asset.id:
            partial_settings = PartialSettingsData(
                assets_to_reset=[original_asset_id],
                assets={updated_asset.id: self.is_asset_enabled(original_asset_id)},
            )
            settings().save(partial_settings, to_global=False)

    async def delete_asset(self, asset_id: str) -> None:
        if not self._storage or not self._notifications:
            _log.error("Assets not configured.")
            raise ValueError("Assets not configured")

        self._notifications.suppress_next_notification()
        await self._storage.delete_asset(asset_id)

    def is_asset_enabled(self, asset_id: str) -> bool:
        if not self._storage or not self._notifications:
            _log.error("Assets not configured.")
            raise ValueError("Assets not configured")

        settings_data = settings().unified_settings

        if asset_id in settings_data.assets:
            status = settings_data.assets[asset_id]
        else:
            asset = self.unified_assets[asset_id][0]
            status = asset.enabled_by_default if asset else True
        return status

    def set_enabled(self, asset_id: str, enabled: bool, to_global: bool = False) -> None:
        settings().save(PartialSettingsData(assets={asset_id: enabled}), to_global=to_global)

    @property
    def is_configured(self):
        return self._storage is not None and self._notifications is not None


@lru_cache
def assets() -> Assets:
    """
    Returns a cached instance of the Assets class.

    :return: A singleton instance of the Assets class.
    """
    return Assets()
