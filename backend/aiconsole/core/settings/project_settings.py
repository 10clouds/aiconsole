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
from pathlib import Path
from typing import Any

import tomlkit
import tomlkit.container
import tomlkit.exceptions
from appdirs import user_config_dir
from pydantic import BaseModel
from tomlkit import TOMLDocument
from watchdog.observers import Observer

from aiconsole.api.websockets.server_messages import SettingsServerMessage
from aiconsole.core.assets.asset import AssetStatus, AssetType
from aiconsole.core.gpt.consts import (
    GPT_MODE_COST_MAX_TOKENS,
    GPT_MODE_COST_MODEL,
    GPT_MODE_QUALITY_MAX_TOKENS,
    GPT_MODE_QUALITY_MODEL,
    GPT_MODE_SPEED_MAX_TOKENS,
    GPT_MODE_SPEED_MODEL,
    GPTEncoding,
    GPTMode,
)
from aiconsole.core.project import project
from aiconsole.core.project.paths import get_project_directory
from aiconsole.core.project.project import is_project_initialized
from aiconsole.utils.BatchingWatchDogHandler import BatchingWatchDogHandler
from aiconsole.utils.recursive_merge import recursive_merge

_log = logging.getLogger(__name__)


class GPTModeConfig(BaseModel):
    name: str
    max_tokens: int = 10000
    encoding: GPTEncoding = GPTEncoding.GPT_4
    model: str | None = None
    api_key: str | None = None
    api_base: str | None = None
    extra: dict[str, Any] = {}


class PartialSettingsData(BaseModel):
    code_autorun: bool | None = None
    openai_api_key: str | None = None
    username: str | None = None
    email: str | None = None
    materials: dict[str, AssetStatus] = {}
    materials_to_reset: list[str] = []
    agents: dict[str, AssetStatus] = {}
    agents_to_reset: list[str] = []
    gpt_modes: dict[str, GPTModeConfig] = {}
    extra: dict[str, Any] = {}
    to_global: bool = False


class PartialSettingsAndToGlobal(PartialSettingsData):
    to_global: bool = False


class SettingsData(BaseModel):
    code_autorun: bool = False
    openai_api_key: str | None = None
    username: str | None = None
    email: str | None = None
    materials: dict[str, AssetStatus] = {}
    agents: dict[str, AssetStatus] = {}
    gpt_modes: dict[str, GPTModeConfig] = {}
    extra: dict[str, Any] = {}


def _load_from_path(file_path: Path) -> dict[str, Any]:
    with file_path.open() as file:
        document = tomlkit.loads(file.read())

    return dict(document)


class Settings:
    def __init__(self, project_path: Path | None = None):
        self._suppress_notification_until = None
        self._settings = SettingsData()

        self._global_settings_file_path = Path(user_config_dir("aiconsole")) / "settings.toml"

        if project_path:
            self._project_settings_file_path = project_path / "settings.toml"
        else:
            self._project_settings_file_path = None

        self._observer = Observer()

        self._global_settings_file_path.parent.mkdir(parents=True, exist_ok=True)
        self._observer.schedule(
            BatchingWatchDogHandler(self.reload, self._global_settings_file_path.name),
            str(self._global_settings_file_path.parent),
            recursive=False,
        )

        if self._project_settings_file_path:
            self._project_settings_file_path.parent.mkdir(parents=True, exist_ok=True)
            self._observer.schedule(
                BatchingWatchDogHandler(self.reload, self._project_settings_file_path.name),
                str(self._project_settings_file_path.parent),
                recursive=False,
            )

        self._observer.start()

    def model_dump(self) -> dict[str, Any]:
        return self._settings.model_dump()

    def stop(self):
        self._observer.stop()

    async def reload(self, initial: bool = False):
        self._settings = await self.__load()
        _log.debug(f"Loaded gpt modes: {self._settings.gpt_modes}")

        await SettingsServerMessage(
            initial=initial
            or not (
                not self._suppress_notification_until or self._suppress_notification_until < datetime.datetime.now()
            )
        ).send_to_all()
        self._suppress_notification_until = None

    def get_asset_status(self, asset_type: AssetType, id: str) -> AssetStatus:
        s = self._settings

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

    def rename_asset(self, asset_type: AssetType, old_id: str, new_id: str):
        if asset_type == AssetType.MATERIAL:
            partial_settings = PartialSettingsData(
                materials_to_reset=[old_id], materials={new_id: self.get_asset_status(asset_type, old_id)}
            )
        elif asset_type == AssetType.AGENT:
            partial_settings = PartialSettingsData(
                agents_to_reset=[old_id], agents={new_id: self.get_asset_status(asset_type, old_id)}
            )
        else:
            raise ValueError(f"Unknown asset type {asset_type}")

        self.save(partial_settings, to_global=True)

    def set_asset_status(self, asset_type: AssetType, id: str, status: AssetStatus, to_global: bool = False) -> None:
        if asset_type == AssetType.MATERIAL:
            self.save(PartialSettingsData(materials={id: status}), to_global=to_global)
        elif asset_type == AssetType.AGENT:
            self.save(PartialSettingsData(agents={id: status}), to_global=to_global)
        else:
            raise ValueError(f"Unknown asset type {asset_type}")

    def get_mode_config(self, gpt_mode: GPTMode) -> GPTModeConfig:
        mode_config = self._settings.gpt_modes.get(gpt_mode, None)

        if mode_config is None:
            raise ValueError(f"Unknown mode {gpt_mode}, available modes: {self._settings.gpt_modes}")

        # if api_key refers to any other setting, use that setting

        for extra in self._settings.extra:
            if mode_config.api_key == extra:
                mode_config = mode_config.model_copy(update={"api_key": self._settings.extra[extra]})

        return mode_config

    def get_code_autorun(self) -> bool:
        return self._settings.code_autorun

    def get_openai_api_key(self) -> str | None:
        return self._settings.openai_api_key

    def get_username(self) -> str | None:
        return self._settings.username

    def get_email(self) -> str | None:
        return self._settings.email

    def set_code_autorun(self, code_autorun: bool, to_global: bool = False) -> None:
        self._settings.code_autorun = code_autorun
        self.save(PartialSettingsData(code_autorun=self._settings.code_autorun), to_global=to_global)

    async def __load(self) -> SettingsData:
        settings = {}
        paths = [self._global_settings_file_path, self._project_settings_file_path]

        for file_path in paths:
            if file_path and file_path.exists():
                settings = recursive_merge(settings, _load_from_path(file_path))

        forced_agents = [agent for agent, status in settings.get("agents", {}).items() if status == AssetStatus.FORCED]

        settings_materials = settings.get("materials", {})

        materials = {}
        for material, status in settings_materials.items():
            materials[material] = AssetStatus(status)

        agents = {}
        for agent, status in settings.get("agents", {}).items():
            agents[agent] = AssetStatus(status)

        # setup default gpt modes
        gpt_modes = {
            "speed": GPTModeConfig(
                name="speed",
                max_tokens=GPT_MODE_SPEED_MAX_TOKENS,
                encoding=GPTEncoding.GPT_4,
                model=GPT_MODE_SPEED_MODEL,
                api_key="openai_api_key",
            ),
            "quality": GPTModeConfig(
                name="quality",
                max_tokens=GPT_MODE_QUALITY_MAX_TOKENS,
                encoding=GPTEncoding.GPT_4,
                model=GPT_MODE_QUALITY_MODEL,
                api_key="openai_api_key",
            ),
            "cost": GPTModeConfig(
                name="cost",
                max_tokens=GPT_MODE_COST_MAX_TOKENS,
                encoding=GPTEncoding.GPT_4,
                model=GPT_MODE_COST_MODEL,
                api_key="openai_api_key",
            ),
        }

        for model_config in settings.get("gpt_modes", []):
            _log.debug(f"Loading gpt mode: {model_config}")
            name = model_config.get("name")
            gpt_modes[name] = GPTModeConfig(**model_config)

        extra_settings = {}
        for key, value in settings.get("settings", {}).items():
            if key not in ["code_autorun"]:
                extra_settings[key] = value

        settings_data = SettingsData(
            code_autorun=settings.get("settings", {}).get("code_autorun", False),
            openai_api_key=settings.get("settings", {}).get("openai_api_key", None),
            username=settings.get("settings", {}).get("username", None),  # Load username
            email=settings.get("settings", {}).get("email", None),  # Load email
            materials=materials,
            agents=agents,
            gpt_modes=gpt_modes,
            extra=extra_settings,
        )

        # Enforce only one forced agent
        if len(forced_agents) > 1:
            _log.warning(f"More than one agent is forced: {forced_agents}")
            for agent in forced_agents[1:]:
                settings_data.agents[agent] = AssetStatus.ENABLED

        _log.info("Loaded settings")
        return settings_data

    @staticmethod
    def __get_tolmdocument_to_save(file_path: Path) -> TOMLDocument:
        if not file_path.exists():
            document = tomlkit.document()
            document["settings"] = tomlkit.table()
            document["materials"] = tomlkit.table()
            document["agents"] = tomlkit.table()
            document["gpt_modes"] = tomlkit.table()
            return document

        with file_path.open() as file:
            document = tomlkit.loads(file.read())
            for section in ["settings", "materials", "agents", "gpt_modes"]:
                if section not in dict(document):
                    document[section] = tomlkit.table()

        return document

    def save(self, settings_data: PartialSettingsData, to_global: bool = False) -> None:
        if to_global:
            global_file_path = self._global_settings_file_path
            file_path = self._global_settings_file_path
        else:
            if settings_data.username is not None and settings_data.email is not None:
                raise ValueError("Username and Email can only be saved in global settings")

            if not self._project_settings_file_path:
                raise ValueError("Cannnot save to project settings file, because project is not initialized")

            global_file_path = self._global_settings_file_path
            file_path = self._project_settings_file_path

        global_document = self.__get_tolmdocument_to_save(global_file_path)
        document = self.__get_tolmdocument_to_save(file_path)
        doc_settings: tomlkit.table.Table = document["settings"]
        doc_materials: tomlkit.table.Table = document["materials"]
        doc_agents: tomlkit.table.Table = document["agents"]
        doc_gpt_modes: tomlkit.table.Table = document["gpt_modes"]
        global_doc_agents: tomlkit.table.Table = global_document["agents"]

        if settings_data.code_autorun is not None:
            doc_settings["code_autorun"] = settings_data.code_autorun

        # write extra
        for key, value in settings_data.extra.items():
            doc_settings[key] = value

        if settings_data.username is not None:
            doc_settings["username"] = settings_data.username

        if settings_data.email is not None:
            doc_settings["email"] = settings_data.email

        for material in settings_data.materials_to_reset:
            if material in doc_materials:
                del doc_materials[material]

        for agent in settings_data.agents_to_reset:
            if agent in doc_agents:
                del doc_agents[agent]

        for material in settings_data.materials:
            doc_materials[material] = settings_data.materials[material].value

        for gpt_mode in settings_data.gpt_modes:
            doc_gpt_modes[gpt_mode] = settings_data.gpt_modes[gpt_mode].model_dump()

        was_forced = False
        for agent in settings_data.agents:
            doc_agents[agent] = settings_data.agents[agent].value
            if settings_data.agents[agent] == AssetStatus.FORCED:
                was_forced = agent

        if was_forced:
            for agent in set([*global_doc_agents, *doc_agents]):
                if agent != was_forced and (
                    doc_agents.get(agent, global_doc_agents.get(agent, "")) == AssetStatus.FORCED.value
                ):
                    doc_agents[agent] = AssetStatus.ENABLED.value

        self._suppress_notification_until = datetime.datetime.now() + datetime.timedelta(seconds=30)

        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open("w") as file:
            file.write(document.as_string())


async def init():
    global _settings
    _settings = Settings(get_project_directory() if is_project_initialized() else None)
    await _settings.reload()


def get_aiconsole_settings() -> Settings:
    return _settings


async def reload_settings(initial: bool = False):
    global _settings
    _settings.stop()
    _settings = Settings(get_project_directory() if is_project_initialized() else None)
    await _settings.reload(initial)
