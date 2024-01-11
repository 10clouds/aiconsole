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

from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import BaseModel

from aiconsole.api.endpoints.projects.registry import project_directory
from aiconsole.api.endpoints.projects.services import ProjectDirectory

router = APIRouter()


class ProjectDirectoryParams(BaseModel):
    directory: str


@router.post("/choose_directory")
async def choose_directory(project_directory: ProjectDirectory = Depends(project_directory)):
    initial_directory = await project_directory.choose_directory()
    return {"directory": None if initial_directory is None else str(initial_directory)}


@router.get("/is_in_directory")
async def is_project_in_directory(directory: str, project_directory: ProjectDirectory = Depends(project_directory)):
    return {"is_project": project_directory.is_project_in_directory(directory)}


@router.post("/switch")
async def switch_project_endpoint(
    params: ProjectDirectoryParams,
    background_tasks: BackgroundTasks,
    project_directory: ProjectDirectory = Depends(project_directory),
):
    await project_directory.switch_or_save_project(params.directory, background_tasks)
