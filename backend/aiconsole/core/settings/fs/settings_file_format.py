from pathlib import Path

import tomlkit
import tomlkit.items

from aiconsole_toolkit.settings.partial_settings_data import PartialSettingsData
from aiconsole_toolkit.settings.settings_data import SettingsData


def load_settings_file(file_path: Path) -> PartialSettingsData:
    document = _get_document(file_path)
    d: dict = dict(document)
    return PartialSettingsData(**d)


def save_settings_file(file_path: Path, settings_data: SettingsData):
    document = _get_document(file_path)
    _update_document(document, settings_data)
    _write_document(file_path, document)


def _get_document(file_path: Path) -> tomlkit.TOMLDocument:
    if not file_path.exists():
        return tomlkit.document()

    with file_path.open("r") as file:
        return tomlkit.loads(file.read())


def _update_document(document: tomlkit.TOMLDocument, settings_data: SettingsData):
    for key, value in settings_data.model_dump().items():
        item = document.get(key)
        if isinstance(item, tomlkit.items.Table) and isinstance(value, dict):
            item.update(value)
        else:
            item = value


def _write_document(file_path: Path, document: tomlkit.TOMLDocument):
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w") as file:
        file.write(document.as_string())
