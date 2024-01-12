import asyncio
from pathlib import Path
from typing import Any

from aiconsole.core.settings.models import PartialSettingsData
from aiconsole.core.settings.project_settings import settings
from aiconsole.core.settings.storage import settings_file_storage


def set_code_autorun(autorun: bool) -> None:
    settings_file_storage().configure(project_path=Path("."))
    settings().configure(storage=settings_file_storage())
    settings().storage.save(PartialSettingsData(code_autorun=autorun))


def get_settings() -> dict[str, Any]:
    asyncio.run(settings().reload())
    return settings().settings_data.model_dump()
