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

from aiconsole.api.websockets.connection_manager import connection_manager
from aiconsole.api.websockets.server_messages import SettingsServerMessage

_log = logging.getLogger(__name__)


class SettingsNotifications:
    def __init__(self):
        self._suppress_notification_until: datetime.datetime | None = None

    def suppress_next_notification(self, seconds: int = 10):
        self._suppress_notification_until = datetime.datetime.now() + datetime.timedelta(minutes=seconds)

    async def notify(self):
        await connection_manager().send_to_all(
            SettingsServerMessage(
                initial=self._suppress_notification_until is not None
                and self._suppress_notification_until > datetime.datetime.now()
            )
        )

        self._suppress_notification_until = None
