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
from functools import lru_cache
from typing import Type

from aiconsole.core.settings.fs.settings_file_storage import SettingsUpdatedEvent
from aiconsole.core.settings.settings_notifications import SettingsNotifications
from aiconsole.core.settings.settings_storage import SettingsStorage
from aiconsole.core.settings.utils.merge_settings_data import merge_settings_data
from aiconsole.utils.events import internal_events
from aiconsole_toolkit.settings.partial_settings_data import PartialSettingsData
from aiconsole_toolkit.settings.settings_data import SettingsData

_log = logging.getLogger(__name__)


class Settings:
    _storage: SettingsStorage | None = None
    _settings_notifications: SettingsNotifications | None = None

    def configure(self, storage_type: Type[SettingsStorage], **kwargs) -> None:
        """
        Configures the settings storage and notifications.

        :param storage_type: The type of settings storage to use.
        :param kwargs: Additional keyword arguments for the storage initialization.
        """
        self.clean_up()

        self._storage = storage_type(**kwargs)
        self._settings_notifications = SettingsNotifications()

        internal_events().subscribe(
            SettingsUpdatedEvent,
            self._when_reloaded,
        )

        if not hasattr(self, "_user_profile_service"):
            from aiconsole.core.users.user import user_profile_service
            self._user_profile_service = user_profile_service()

        self._user_profile_service.configure_user()

        _log.info("Settings configured")

    def clean_up(self) -> None:
        """
        Cleans up resources used by the settings, such as storage and notifications.
        """
        if self._storage:
            self._storage.destroy()

        self._storage = None
        self._settings_notifications = None

        internal_events().unsubscribe(
            SettingsUpdatedEvent,
            self._when_reloaded,
        )

    async def _when_reloaded(self, SettingsUpdatedEvent) -> None:
        """
        Handles the settings updated event asynchronously.

        :param SettingsUpdatedEvent: The event indicating that settings have been updated.
        """
        if not self._storage or not self._settings_notifications:
            _log.error("Settings not configured.")
            raise ValueError("Settings not configured")

        await self._settings_notifications.notify()

    @property
    def unified_settings(self) -> SettingsData:
        """
        Merges global and project settings into a unified settings object.

        :return: A unified settings data object.
        """
        if not self._storage or not self._settings_notifications:
            _log.error("Settings not configured.")
            raise ValueError("Settings not configured")

        return merge_settings_data(self._storage.global_settings, self._storage.project_settings)

    def save(self, settings_data: PartialSettingsData, to_global: bool) -> None:
        """
        Saves the provided settings data either globally or at the project level.

        :param settings_data: The settings data to save.
        :param to_global: True to save settings globally, False to save them at the project level.
        """
        if not self._storage or not self._settings_notifications:
            _log.error("Settings not configured.")
            raise ValueError("Settings not configured")

        self._settings_notifications.suppress_next_notification()
        self._storage.save(settings_data, to_global=to_global)


@lru_cache
def settings() -> Settings:
    """
    Returns a cached instance of the Settings class.

    :return: A singleton instance of the Settings class.
    """
    return Settings()
