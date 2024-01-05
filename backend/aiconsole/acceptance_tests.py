from pathlib import Path

import pytest
from fastapi import BackgroundTasks

from aiconsole.core.gpt.check_key import cached_good_keys, check_key
from aiconsole.core.project.project import choose_project
from aiconsole.core.recent_projects.recent_projects import get_recent_project
from aiconsole.core.settings import project_settings


@pytest.fixture
def background_tasks() -> BackgroundTasks:
    return BackgroundTasks()


@pytest.mark.asyncio
async def test_should_be_able_to_add_new_project(background_tasks: BackgroundTasks):
    await _initialize_app()
    _login("test_key")

    project_path = Path("./")

    await choose_project(
        path=project_path,
        background_tasks=background_tasks,
    )

    assert project_path.absolute() in {project.path.absolute() for project in await get_recent_project()}


async def _initialize_app():
    await project_settings.init()


def _login(openai_api_key: str):
    cached_good_keys.add(openai_api_key)
    check_key(openai_api_key)
