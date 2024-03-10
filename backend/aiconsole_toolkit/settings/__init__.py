from pathlib import Path

from aiconsole_toolkit.settings.partial_settings_data import PartialSettingsData
from aiconsole_toolkit.settings.settings_data import SettingsData


def set_code_autorun(autorun: bool) -> None:
    from aiconsole.core.settings.fs.settings_file_storage import SettingsFileStorage
    from aiconsole.core.settings.settings import settings

    settings().configure(SettingsFileStorage, project_path=Path("."))
    settings().save(PartialSettingsData(code_autorun=autorun), to_global=True)


def get_settings() -> SettingsData:
    from aiconsole.core.settings.fs.settings_file_storage import SettingsFileStorage
    from aiconsole.core.settings.settings import settings

    settings().configure(SettingsFileStorage, project_path=Path("."), disable_observer=True)
    return settings().unified_settings
