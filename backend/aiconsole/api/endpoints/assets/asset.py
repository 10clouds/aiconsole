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

from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from aiconsole.api.endpoints.registry import assets
from aiconsole.api.endpoints.services import (
    AssetsService,
    AssetWithGivenNameAlreadyExistError,
)
from aiconsole.core.assets.agents.agent import AICAgent
from aiconsole.core.assets.assets import Assets
from aiconsole.core.assets.fs.exceptions import UserIsAnInvalidAgentIdError
from aiconsole.core.assets.get_material_content_name import get_material_content_name
from aiconsole.core.assets.materials.material import AICMaterial, MaterialContentType
from aiconsole.core.assets.types import Asset, AssetLocation, AssetType
from aiconsole.core.chat.load_chat_history import load_chat_history
from aiconsole.core.chat.save_chat_history import save_chat_history
from aiconsole.core.chat.types import AICChat
from aiconsole.core.project import project
from aiconsole.core.project.paths import (
    get_core_assets_directory,
    get_history_directory,
    get_project_assets_directory,
)
from aiconsole.core.project.project import is_project_initialized

router = APIRouter()

DeserializableAsset = AICAgent | AICMaterial | AICChat


@router.get("/{asset_id}")
async def get_asset(request: Request, asset_id: str):
    location_param = request.query_params.get("location", None)
    location = AssetLocation(location_param) if location_param else None

    if asset_id == "new":
        type_raw = request.query_params.get("type", None)

        if type_raw is None:
            raise HTTPException(status_code=400, detail="Type not specified")

        type = AssetType(type_raw)

        asset: Asset | None

        if type == "agent":
            asset = AICAgent(
                id="new_agent",
                name="New Agent",
                usage="",
                usage_examples=[],
                enabled=True,
                defined_in=AssetLocation.PROJECT_DIR,
                system="",
                override=False,
                last_modified=datetime.now(),
            )
        elif type == "material":
            content_type_raw = request.query_params.get("content_type", None)

            if content_type_raw is None:
                raise HTTPException(status_code=400, detail="Content type not specified")

            content_type = MaterialContentType(content_type_raw)

            asset = AICMaterial(
                id="new_" + get_material_content_name(content_type).lower(),
                name="New " + get_material_content_name(content_type),
                content_type=content_type,
                usage="",
                usage_examples=[],
                enabled=True,
                defined_in=AssetLocation.PROJECT_DIR,
                override=False,
                content=get_default_content_for_type(content_type),
                last_modified=datetime.now(),
            )
        elif type == "chat":
            asset = await load_chat_history(id=str(uuid4()))
            asset.id = "new_chat"
            asset.defined_in = AssetLocation.PROJECT_DIR
            asset.override = False
        else:
            raise HTTPException(status_code=400, detail="Invalid type")

        return JSONResponse(asset.model_dump(exclude_none=True))
    else:
        assets = project.get_project_assets()

        asset = assets.get_asset(asset_id, location)

        if not asset:
            raise HTTPException(status_code=404, detail=f"{asset_id} not found")

        if isinstance(asset, AICMaterial):
            asset.content = asset.inlined_content

        return JSONResponse(
            {
                **asset.model_dump(),
                "status": assets.is_enabled(asset.id),
            }
        )


"""
TODO: This is conflicting
"""


@router.patch("/{asset_id}")
async def partially_update_asset(
    asset_id: str, asset: DeserializableAsset, agents_service: AssetsService = Depends(assets)
):
    try:
        if asset.type == AssetType.CHAT:
            chat = await load_chat_history(id=asset_id)
            if asset.name:
                chat.name = str(asset.name)
                await save_chat_history(chat, scope="name")
                await project.get_project_assets().reload(initial=True)
        else:
            await agents_service.partially_update_asset(asset_id=asset_id, asset=asset)

    except AssetWithGivenNameAlreadyExistError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Asset with given name already exists")
    except UserIsAnInvalidAgentIdError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot create agent with 'user' name")


@router.post("/{asset_id}")
async def create_asset(asset_id: str, asset: DeserializableAsset, agents_service: AssetsService = Depends(assets)):
    try:
        await agents_service.cretate_asset(asset_id=asset_id, asset=asset)
    except AssetWithGivenNameAlreadyExistError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Agent with given name already exists")
    except UserIsAnInvalidAgentIdError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot create agent with 'user' name")


@router.delete("/{asset_id}")
async def delete_asset(asset_id: str):
    try:
        await project.get_project_assets().delete_asset(asset_id)
        return JSONResponse({"status": "ok"})
    except KeyError:
        raise HTTPException(status_code=404, detail="Asset not found")


class EnabledFlagChangePostBody(BaseModel):
    enabled: bool
    to_global: bool


@router.post("/{asset_id}/status-change")
async def asset_status_change(asset_id: str, body: EnabledFlagChangePostBody):
    try:
        Assets.set_enabled(id=asset_id, enabled=body.enabled, to_global=body.to_global)
        return JSONResponse({"status": "ok"})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{asset_id}/exists")
async def asset_exists(request: Request, asset_id: str):
    location_param = request.query_params.get("location", None)
    location = AssetLocation(location_param) if location_param else None

    if not location:
        raise HTTPException(status_code=400, detail="Location not specified")

    if asset_id == "new":
        return JSONResponse({"exists": False})
    else:
        assets = project.get_project_assets()

        asset = assets.get_asset(asset_id, location)

        return JSONResponse({"exists": asset is not None})


@router.get("/{asset_id}/path")
async def asset_path(request: Request, asset_id: str):
    asset = project.get_project_assets().get_asset(asset_id)

    if asset is None:
        raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")

    if asset.type == AssetType.CHAT:
        path = get_history_directory() / f"{asset_id}.json"
    else:
        path = get_project_assets_directory(asset.type) / f"{asset_id}.toml"

    return JSONResponse({"path": str(path)})


@router.get("/{asset_id}/image")
async def profile_image(asset_id: str):
    asset = project.get_project_assets().get_asset(asset_id)

    if asset:
        if is_project_initialized():
            image_path = get_project_assets_directory(asset.type) / f"{asset_id}.jpg"

            if image_path.exists():
                return FileResponse(str(image_path))

        static_path = get_core_assets_directory(asset.type) / f"{asset_id}.jpg"
        if static_path.exists():
            return FileResponse(str(static_path))

    default_path = get_core_assets_directory(AssetType.AGENT) / "default.jpg"
    return FileResponse(str(default_path))


@router.post("/{asset_id}/avatar")
async def set_avatar(asset_id: str, avatar: UploadFile = File(...), agents_service: AssetsService = Depends(assets)):
    await agents_service.set_avatar(asset_id=asset_id, avatar=avatar)


def get_default_content_for_type(type: MaterialContentType):
    if type == MaterialContentType.STATIC_TEXT:
        return """

content, content content

## Sub header

Bullets in sub header:
* Bullet 1
* Bullet 2
* Bullet 3

""".strip()
    elif type == MaterialContentType.DYNAMIC_TEXT:
        return """

import random

async def content(context):
    samples = ['sample 1' , 'sample 2', 'sample 3', 'sample 4']
    return f'''
# Examples of great content
{random.sample(samples, 2)}

'''.strip()

""".strip()
    elif type == MaterialContentType.API:
        return """

'''
Add here general API description
'''

def create():
    '''
    Add comment when to use this function, and add example of usage:
    ```python
        create()
    ```
    '''
    print("Created")


def print_list():
    '''
    Use this function to print 'List'.
    Sample of use:
    ```python
        print_list()
    ```

    '''
    print("List")



def fibonacci(n):
    '''
    Use it to calculate and return the nth term of the Fibonacci sequence.
    Sample of use:
    ```python
      fibonacci(10)
    ```
    '''
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    return fibonacci(n - 1) + fibonacci(n - 2)
""".strip()
    else:
        raise ValueError("Invalid material content type")
