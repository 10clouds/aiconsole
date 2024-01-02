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
from typing import Optional
import requests
from pydantic import BaseModel
from fastapi import APIRouter
from libgravatar import Gravatar

DEFAULT_AVATAR_URL = "https://gravatar.com/avatar/?d=mp"


class UserProfile(BaseModel):
    username: str
    avatar_url: str


router = APIRouter()


@router.get("/profile", response_model=UserProfile)
def profile(email: Optional[str] = None):
    if not email:
        return UserProfile(username=f"user", avatar_url=DEFAULT_AVATAR_URL)

    gravatar = Gravatar(email)
    url_profile_json = gravatar.get_profile(data_format="json")
    response = requests.get(url_profile_json)

    if response.status_code == 200:
        gravatar_data = response.json()

        entry = gravatar_data["entry"][0]
        user_profile = UserProfile(
            username=entry.get("preferredUsername", ""), avatar_url=entry.get("thumbnailUrl", "")
        )
        return user_profile
    else:
        return UserProfile(username=f"{email}", avatar_url=DEFAULT_AVATAR_URL)
