import logging
from functools import lru_cache
from pathlib import Path
from typing import Optional

import tomlkit

from aiconsole.consts import AICONSOLE_USER_CONFIG_DIR
from aiconsole.core.settings import models
from aiconsole.core.settings.base.storage import SettingsStorage
from aiconsole.core.settings.observer import FileObserver

_log = logging.getLogger(__name__)


class SettingsFileStorage(SettingsStorage):
    def configure(
        self,
        project_path: Optional[Path] = None,
        observer: Optional[FileObserver] = FileObserver(),
    ):
        self.observer = observer
        self.change_project(project_path)
        _log.debug(f"{self.__class__.__name__} was configured")

    @property
    def global_settings_file_path(self):
        return AICONSOLE_USER_CONFIG_DIR() / "settings.toml"

    @property
    def project_settings_file_path(self):
        return self._project_settings_file_path

    @property
    def global_settings(self):
        return self._get_settings_from_path(self.global_settings_file_path)

    @property
    def project_settings(self):
        return self._get_settings_from_path(self.project_settings_file_path)

    def change_project(self, project_path: Optional[Path] = None):
        self._project_settings_file_path = project_path / "settings.toml" if project_path else None
        self.load()
        self._start_observer()

    def save(self, settings_data: models.PartialSettingsData):
        file_path = self.global_settings_file_path if settings_data.to_global else self.project_settings_file_path
        if not file_path:
            raise ValueError("Cannot save settings, path not specified")

        document = self._get_document(file_path)
        self._update_document(document, settings_data)
        self._write_document(file_path, document)

    def _start_observer(self):
        from aiconsole.core.settings.project_settings import settings

        file_paths = [self.global_settings_file_path]
        if self.project_settings_file_path:
            file_paths.append(self.project_settings_file_path)

        if self.observer:
            self.observer.start(file_paths=file_paths, action=settings().reload)

    @staticmethod
    def _get_settings_from_path(file_path: Path | None) -> dict:
        if file_path:
            data = dict(settings_file_storage()._get_document(file_path))
        else:
            data = dict()
        return data

    @staticmethod
    def _get_document(file_path: Path) -> tomlkit.TOMLDocument:
        if not file_path.exists():
            return tomlkit.document()

        with file_path.open("r") as file:
            return tomlkit.loads(file.read())

    @staticmethod
    def _update_document(document: tomlkit.TOMLDocument, settings_data: models.PartialSettingsData):
        for key, value in settings_data.model_dump(exclude_none=True, exclude={"to_global"}).items():
            if isinstance(document.get(key), tomlkit.items.Table) and isinstance(value, dict):  # type: ignore
                document[key].update(value)  # type: ignore
            else:
                document[key] = value

    @staticmethod
    def _write_document(file_path: Path, document: tomlkit.TOMLDocument):
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open("w") as file:
            file.write(document.as_string())


@lru_cache
def settings_file_storage() -> SettingsFileStorage:
    return SettingsFileStorage()
