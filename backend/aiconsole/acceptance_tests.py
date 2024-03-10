from pathlib import Path

import pytest
from fastapi import BackgroundTasks

from aiconsole.api.endpoints.projects.services import ProjectDirectory
from aiconsole.core.gpt.check_key import cached_good_keys, check_key
from aiconsole.core.recent_projects.recent_projects import get_recent_project
from aiconsole.core.settings.fs.settings_file_storage import SettingsFileStorage
from aiconsole.core.settings.settings import settings


@pytest.fixture
def background_tasks() -> BackgroundTasks:
    return BackgroundTasks()


@pytest.fixture
def project_directory() -> ProjectDirectory:
    return ProjectDirectory()


@pytest.mark.asyncio
async def test_should_be_able_to_add_new_project(
    background_tasks: BackgroundTasks, project_directory: ProjectDirectory
):
    await _initialize_app()
    await _login("test_key")

    project_path = Path("./")

    await project_directory.switch_or_save_project(
        directory=str(project_path),
        background_tasks=background_tasks,
    )

    assert project_path.absolute() in {project.path.absolute() for project in await get_recent_project()}


async def _initialize_app():
    settings().configure(SettingsFileStorage, project_path=None)


async def _login(openai_api_key: str):
    cached_good_keys.add(openai_api_key)
    check_key(openai_api_key)
