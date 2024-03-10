import logging
import os
from collections import defaultdict
from pathlib import Path

from aiconsole.api.websockets.connection_manager import connection_manager
from aiconsole.api.websockets.server_messages import ErrorServerMessage
from aiconsole.core.assets.fs.load_asset_from_fs import load_asset_from_fs
from aiconsole.core.assets.types import Asset, AssetLocation, AssetType
from aiconsole.core.chat.list_possible_historic_chat_ids import (
    list_possible_historic_chat_ids,
)
from aiconsole.core.chat.load_chat_history import load_chat_history
from aiconsole.core.project.paths import (
    get_core_assets_directory,
    get_project_assets_directory,
)
from aiconsole.utils.list_files_in_file_system import list_files_in_file_system

_log = logging.getLogger(__name__)


async def load_all_assets(asset_type: AssetType) -> dict[str, list[Asset]]:
    _assets: dict[str, list[Asset]] = defaultdict(list)

    if asset_type == AssetType.CHAT:
        for chat_id in list_possible_historic_chat_ids():
            try:
                chat = await load_chat_history(chat_id)

                if chat:
                    _assets[chat_id].append(chat)

            except Exception as e:
                _log.exception(e)
                _log.error(f"Failed to get history: {e} {chat_id}")
    else:
        locations = [
            [AssetLocation.PROJECT_DIR, get_project_assets_directory(asset_type)],
            [AssetLocation.AICONSOLE_CORE, get_core_assets_directory(asset_type)],
        ]

        for [location, dir] in locations:
            ids = set(
                [
                    os.path.splitext(os.path.basename(path))[0]
                    for path in list_files_in_file_system(dir)
                    if os.path.splitext(Path(path))[-1] == ".toml"
                ]
            )

            for id in ids:
                try:
                    _assets[id].append(await load_asset_from_fs(asset_type, id, location))
                except Exception as e:
                    await connection_manager().send_to_all(
                        ErrorServerMessage(
                            error=f"Invalid {asset_type} {id} {e}",
                        )
                    )
                    continue

    return _assets
