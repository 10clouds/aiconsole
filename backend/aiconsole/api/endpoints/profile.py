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

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from aiconsole.core.users.models import UserProfile
from aiconsole.core.users.user import UserProfileService, user_profile_service

router = APIRouter()


@router.get("/profile", response_model=UserProfile)
def profile(
    email: Optional[str] = None, user_profile_service: UserProfileService = Depends(user_profile_service)
) -> UserProfile:
    return user_profile_service.get_profile(email=email)


@router.get("/profile_image")
def profile_image(
    img_filename: str, user_profile_service: UserProfileService = Depends(user_profile_service)
) -> FileResponse:
    file_path = user_profile_service.get_profile_image_path(img_filename)
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(str(file_path))
