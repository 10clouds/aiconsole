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

from typing import cast

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from aiconsole.api.endpoints.registry import materials
from aiconsole.api.endpoints.services import (
    AssetWithGivenNameAlreadyExistError,
    Materials,
)
from aiconsole.api.utils.asset_exists import asset_exists, asset_path
from aiconsole.api.utils.asset_get import asset_get
from aiconsole.api.utils.asset_status_change import asset_status_change
from aiconsole.api.utils.status_change_post_body import StatusChangePostBody
from aiconsole.core.assets.get_material_content_name import get_material_content_name
from aiconsole.core.assets.materials.material import (
    Material,
    MaterialContentType,
    MaterialWithStatus,
)
from aiconsole.core.assets.models import AssetLocation, AssetStatus, AssetType
from aiconsole.core.project import project

router = APIRouter()


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


@router.get("/{material_id}")
async def get_material(request: Request, material_id: str):
    type = cast(MaterialContentType, request.query_params.get("type", ""))

    return await asset_get(
        request,
        AssetType.MATERIAL,
        material_id,
        lambda: MaterialWithStatus(
            id="new_" + get_material_content_name(type).lower(),
            name="New " + get_material_content_name(type),
            content_type=type,
            usage="",
            usage_examples=[],
            status=AssetStatus.ENABLED,
            defined_in=AssetLocation.PROJECT_DIR,
            override=False,
            content=get_default_content_for_type(type),
        ),
    )


@router.patch("/{asset_id}")
async def partially_update_material(
    asset_id: str, material: Material, materials_service: Materials = Depends(materials)
):
    try:
        await materials_service.partially_update_material(material_id=asset_id, material=material)
    except AssetWithGivenNameAlreadyExistError:
        raise HTTPException(status_code=400, detail="Material with given name already exists")


@router.post("/{asset_id}")
async def create_material(asset_id: str, material: Material, materials_service: Materials = Depends(materials)):
    try:
        await materials_service.create_material(material_id=asset_id, material=material)
    except AssetWithGivenNameAlreadyExistError:
        raise HTTPException(status_code=400, detail="Material with given name already exists")


@router.post("/{material_id}/status-change")
async def material_status_change(material_id: str, body: StatusChangePostBody):
    return await asset_status_change(AssetType.MATERIAL, material_id, body)


@router.delete("/{material_id}")
async def delete_material(material_id: str):
    try:
        await project.get_project_materials().delete_asset(material_id)
        return JSONResponse({"status": "ok"})
    except KeyError:
        raise HTTPException(status_code=404, detail="Material not found")


@router.get("/{asset_id}/exists")
async def material_exists(request: Request, asset_id: str):
    return await asset_exists(AssetType.MATERIAL, request, asset_id)


@router.get("/{asset_id}/path")
async def material_path(request: Request, asset_id: str):
    return asset_path(AssetType.MATERIAL, request, asset_id)
