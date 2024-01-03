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
import hashlib
import requests
from typing import Optional
from pathlib import Path
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from aiconsole.core.settings.project_settings import get_aiconsole_settings
from aiconsole.utils.resource_to_path import resource_to_path
from libgravatar import Gravatar

AVATARS_PATH = "aiconsole.preinstalled.avatars"

router = APIRouter()


class UserProfile(BaseModel):
    username: str = "user"
    avatar_url: Optional[str] = None
    gravatar: bool = False


def deterministic_choice(blob: str, choices: list[Path]) -> Path:
    hash_value = hashlib.sha256(blob.encode()).hexdigest()
    choice_index = int(hash_value, 16) % len(choices)
    return choices[choice_index]


@router.get("/profile", response_model=UserProfile)
def profile(email: Optional[str] = None) -> UserProfile:
    if not email:
        img_filename = deterministic_choice(
            get_aiconsole_settings().get_openai_api_key() or "some_key", list(resource_to_path(AVATARS_PATH).glob("*"))
        ).name
        return UserProfile(avatar_url=f"/profile_image?img_filename={img_filename}")

    gravatar = Gravatar(email)
    url_profile_json = gravatar.get_profile(data_format="json")
    try:
        response = requests.get(url_profile_json)
        response.raise_for_status()
        gravatar_data = response.json()
        entry = gravatar_data["entry"][0]
        return UserProfile(
            username=entry.get("preferredUsername", email), avatar_url=entry.get("thumbnailUrl", ""), gravatar=True
        )
    except requests.RequestException:
        img_filename = deterministic_choice(email, list(resource_to_path(AVATARS_PATH).glob("*"))).name
        return UserProfile(username=email, avatar_url=f"/profile_image?img_filename={img_filename}")


@router.get("/profile_image")
def default_profile_image(img_filename: str) -> FileResponse:
    file_path = resource_to_path(AVATARS_PATH) / img_filename
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(str(file_path))
