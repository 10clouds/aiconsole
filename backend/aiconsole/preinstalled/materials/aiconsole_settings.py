"""
Use this material to change AIConsole settings.

Available settings are:
1. code_autorun - boolean.

Tell user what setting are available if user will want to set something.

"""

from aiconsole_toolkit import settings
from aiconsole_toolkit.settings.settings_data import SettingsData


def set_code_autorun(autorun: bool) -> None:
    """
    Use it do set code_autorun in AIConsole settings. Do not use anything else to set code_autorun
    """
    settings.set_code_autorun(autorun)


def get_settings() -> SettingsData:
    """
    Use it to know what AIConsole settings you have access to.
    You'll get a dict "key: value" where key is a name of setting, and value which is the value of the setting.
    """
    return settings.get_settings()
