from aiconsole_toolkit.settings.partial_settings_data import PartialSettingsData
from aiconsole_toolkit.settings.settings_data import SettingsData


def update_settings_data(settings: SettingsData, *new_settings: PartialSettingsData):
    settings_data = settings.model_dump()

    for new_setting in new_settings:
        settings_data.update(new_setting.model_dump(exclude_unset=True))

    return SettingsData(**settings_data)
