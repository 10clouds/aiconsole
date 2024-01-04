import hashlib
from pathlib import Path

from aiconsole.core.users.gravatar import GravatarProfileService
from aiconsole.core.users.models import UserProfile
from aiconsole.utils.resource_to_path import resource_to_path
from aiconsole.core.settings.project_settings import get_aiconsole_settings

AVATARS_PATH = "aiconsole.preinstalled.avatars"

DEFAULT_USERNAME = "User"


class UserProfileService:
    @staticmethod
    def get_profile(email: str | None = None) -> UserProfile:
        if email is not None and (profile := GravatarProfileService.get_gravatar_profile(email)):
            return profile

        return UserProfile(
            username=email if email else DEFAULT_USERNAME,
            email=email,
            avatar_url=UserProfileService._get_default_avatar(email=email)
            if email
            else UserProfileService._get_default_avatar(),
            gravatar=False,
        )

    @staticmethod
    def get_profile_image_path(img_filename: str):
        return resource_to_path(AVATARS_PATH) / img_filename

    @staticmethod
    def _get_default_avatar(email: str | None = None) -> str:
        key = email or get_aiconsole_settings().get_openai_api_key() or "some_key"
        img_filename = UserProfileService._deterministic_choice(
            key, list(resource_to_path(AVATARS_PATH).glob("*"))
        ).name
        return f"/profile_image?img_filename={img_filename}"

    @staticmethod
    def _deterministic_choice(blob: str, choices: list[Path]) -> Path:
        hash_value = hashlib.sha256(blob.encode()).hexdigest()
        choice_index = int(hash_value, 16) % len(choices)
        return choices[choice_index]
