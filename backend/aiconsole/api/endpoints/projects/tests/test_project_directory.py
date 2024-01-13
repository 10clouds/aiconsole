import pytest
from fastapi import BackgroundTasks

from aiconsole.api.endpoints.projects.services import ProjectDirectory


@pytest.fixture
def project_directory() -> ProjectDirectory:
    return ProjectDirectory()


@pytest.mark.asyncio
async def test_should_project_be_in_directory_when_added(
    project_directory: ProjectDirectory,
):
    initial_directory = "./"

    await project_directory.switch_or_save_project(directory=initial_directory, background_tasks=BackgroundTasks())

    assert project_directory.is_project_in_directory(initial_directory)
