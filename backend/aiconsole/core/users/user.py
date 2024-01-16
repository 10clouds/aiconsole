import hashlib
from functools import lru_cache
from mimetypes import guess_extension
from pathlib import Path
from typing import BinaryIO

from aiconsole.consts import AICONSOLE_USER_CONFIG_DIR
from aiconsole.core.clients.gravatar import GravatarUserProfile, gravatar_client
from aiconsole.core.settings.settings import settings
from aiconsole.core.users.models import (
    DEFAULT_USERNAME,
    PartialUserProfile,
    UserProfile,
)
from aiconsole.utils.resource_to_path import resource_to_path
from aiconsole_toolkit.settings.partial_settings_data import PartialSettingsData

DEFAULT_AVATARS_PATH = "aiconsole.preinstalled.avatars"


class MissingFileName(Exception):
    """File name is missing"""


class UserProfileService:
    def get_profile(self, email: str | None = None) -> UserProfile:
        user_profile = settings().unified_settings.user_profile
        if email:
            if email == user_profile.email and user_profile.avatar_url:
                return user_profile

            gravatar_profile = gravatar_client().get_profile(email)
            if gravatar_profile:
                return self._create_user_profile_from_gravatar(email, gravatar_profile)

        return UserProfile(
            username=email or DEFAULT_USERNAME,
            email=email,
            avatar_url=self._get_default_avatar(email) if email else self._get_default_avatar(),
            gravatar=False,
        )

    def save_avatar(
        self,
        file: BinaryIO,
        file_name: str | None = None,
        content_type: str | None = None,
    ) -> None:
        extension = guess_extension(content_type) if content_type else None
        if not file_name:
            if not extension:
                raise MissingFileName()
            file_name = f"avatar{extension}"

        file_path = self.get_avatar(file_name)
        self._save_avatar_to_fs(file, file_path)

        avatar_url = f"profile_image?img_filename={file_path.name}"
        settings().save(
            PartialSettingsData(
                user_profile=PartialUserProfile(avatar_url=avatar_url),
            ),
            to_global=True,
        )

    def get_avatar(self, img_filename: str) -> Path:
        return self.get_avatar_folder_path() / img_filename

    @staticmethod
    def get_avatar_folder_path() -> Path:
        avatar_folder_path = AICONSOLE_USER_CONFIG_DIR() / "avatars"
        avatar_folder_path.mkdir(parents=False, exist_ok=True)
        return avatar_folder_path

    @staticmethod
    def get_profile_image_path(img_filename: str) -> Path:
        return resource_to_path(DEFAULT_AVATARS_PATH) / img_filename

    def _get_default_avatar(self, email: str | None = None) -> str:
        key = email or settings().unified_settings.openai_api_key or "some_key"
        img_filename = self._deterministic_choice(
            blob=key,
            choices=list(resource_to_path(resource=DEFAULT_AVATARS_PATH).glob(pattern="*")),
        ).name
        return f"profile_image?img_filename={img_filename}"

    def _create_user_profile_from_gravatar(self, email: str, gravatar_profile: GravatarUserProfile) -> UserProfile:
        return UserProfile(
            username=gravatar_profile.preferredUsername,
            email=email,
            avatar_url=gravatar_profile.thumbnailUrl,
            gravatar=True,
        )

    def _save_avatar_to_fs(self, file: BinaryIO, file_path: Path) -> None:
        with open(file_path, "wb+") as file_object:
            file_object.write(file.read())

    def _deterministic_choice(self, blob: str, choices: list[Path]) -> Path:
        hash_value = hashlib.sha256(string=blob.encode()).hexdigest()
        choice_index = int(hash_value, base=16) % len(choices)
        return choices[choice_index]


@lru_cache
def user_profile_service() -> UserProfileService:
    return UserProfileService()
