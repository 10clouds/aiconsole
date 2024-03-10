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
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from aiconsole.core.users.types import UserProfile
from aiconsole.core.users.user import (
    MissingFileName,
    UserProfileService,
    user_profile_service,
)

router = APIRouter()


@router.get("/profile", response_model=UserProfile)
def profile(
    user_id: str,
    user_profile_service: UserProfileService = Depends(dependency=user_profile_service),
) -> UserProfile:
    return user_profile_service.get_profile(user_id)


@router.post("/profile_image", status_code=status.HTTP_201_CREATED)
def set_profile_image(
    avatar: UploadFile = File(...),
    user_profile_service: UserProfileService = Depends(dependency=user_profile_service),
):
    try:
        user_profile_service.save_avatar(
            file=avatar.file,
            file_name=avatar.filename,
            content_type=avatar.content_type,
        )
    except MissingFileName:
        return HTTPException(status_code=400, detail="Missing a file name.")
