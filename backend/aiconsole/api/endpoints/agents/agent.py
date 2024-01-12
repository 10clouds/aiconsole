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

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import FileResponse, JSONResponse

from aiconsole.api.endpoints.registry import agents
from aiconsole.api.endpoints.services import Agents, AssetWithGivenNameAlreadyExistError
from aiconsole.api.utils.asset_exists import asset_exists, asset_path
from aiconsole.api.utils.asset_get import asset_get
from aiconsole.api.utils.asset_status_change import asset_status_change
from aiconsole.api.utils.status_change_post_body import StatusChangePostBody
from aiconsole.core.assets.agents.agent import Agent, AgentWithStatus
from aiconsole.core.assets.asset import AssetLocation, AssetStatus, AssetType
from aiconsole.core.gpt.consts import QUALITY_GPT_MODE
from aiconsole.core.project import project
from aiconsole.core.project.paths import (
    get_core_assets_directory,
    get_project_assets_directory,
)
from aiconsole.core.project.project import is_project_initialized

router = APIRouter()


@router.get("/{agent_id}")
async def get_agent(request: Request, agent_id: str):
    return await asset_get(
        request,
        AssetType.AGENT,
        agent_id,
        lambda: AgentWithStatus(
            id="new_agent",
            name="New Agent",
            usage="",
            usage_examples=[],
            status=AssetStatus.ENABLED,
            defined_in=AssetLocation.PROJECT_DIR,
            gpt_mode=QUALITY_GPT_MODE,
            system="",
            override=False,
        ),
    )


@router.patch("/{agent_id}")
async def partially_update_agent(agent_id: str, agent: Agent, agents_service: Agents = Depends(agents)):
    try:
        await agents_service.partially_update_agent(agent_id=agent_id, agent=agent)
    except AssetWithGivenNameAlreadyExistError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Agent with given name already exists")


@router.post("/{agent_id}")
async def create_agent(agent_id: str, agent: Agent, agents_service: Agents = Depends(agents)):
    try:
        await agents_service.create_agent(agent_id=agent_id, agent=agent)
    except AssetWithGivenNameAlreadyExistError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Agent with given name already exists")


@router.post("/{agent_id}/status-change")
async def agent_status_change(agent_id: str, body: StatusChangePostBody):
    await asset_status_change(AssetType.AGENT, agent_id, body)


@router.delete("/{agent_id}")
async def delete_agent(agent_id: str):
    try:
        await project.get_project_agents().delete_asset(agent_id)
        return JSONResponse({"status": "ok"})
    except KeyError:
        raise HTTPException(status_code=404, detail="Agent not found")


@router.get("/{asset_id}/exists")
async def agent_exists(request: Request, asset_id: str):
    return await asset_exists(AssetType.AGENT, request, asset_id)


@router.get("/{asset_id}/path")
async def agent_path(request: Request, asset_id: str):
    return asset_path(AssetType.AGENT, request, asset_id)


@router.get("/{asset_id}/image")
async def profile_image(asset_id: str):
    if is_project_initialized():
        image_path = get_project_assets_directory(AssetType.AGENT) / f"{asset_id}.jpg"

        if image_path.exists():
            return FileResponse(str(image_path))

    static_path = get_core_assets_directory(AssetType.AGENT) / f"{asset_id}.jpg"
    if static_path.exists():
        return FileResponse(str(static_path))

    default_path = get_core_assets_directory(AssetType.AGENT) / "default.jpg"
    return FileResponse(str(default_path))
