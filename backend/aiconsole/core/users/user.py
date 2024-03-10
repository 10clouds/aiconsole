import base64
import hashlib
import logging
from functools import lru_cache
from mimetypes import guess_type
from pathlib import Path
from uuid import uuid4
from aiconsole.core.assets.types import AssetType

from aiconsole.core.assets.users.users import AICUserProfile
from aiconsole.core.project import project
from aiconsole.core.settings.settings import settings
from aiconsole.core.users.types import PartialUserProfile, UserProfile
from aiconsole.utils.resource_to_path import resource_to_path
from aiconsole_toolkit.settings.partial_settings_data import PartialSettingsData

_log = logging.getLogger(__name__)


DEFAULT_AVATARS_PATH = "aiconsole.preinstalled.avatars"
DEFAULT_USERNAME = "User"


class MissingFileName(Exception):
    """File name is missing"""


class UserProfileService:
    def configure_user(self):
        user_profile = settings().unified_settings.user_profile
        if user_profile is None:
            user_id = str(uuid4())
            settings().save(
                PartialSettingsData(
                    user_profile=PartialUserProfile(
                        id=user_id, display_name=DEFAULT_USERNAME, profile_picture=self.get_default_avatar(user_id)
                    )
                ),
                to_global=True,
            )

    def get_profile(self, user_id: str | None = None) -> UserProfile:
        user_profile = settings().unified_settings.user_profile
        if user_profile and user_profile.id == user_id:
            return user_profile

        aic_user_profile: AICUserProfile | None = project.get_project_assets().get_asset(id=user_id, type=AssetType.USER)  # type: ignore
        if aic_user_profile:
            return UserProfile(
                id=aic_user_profile.id,
                display_name=aic_user_profile.display_name,
                profile_picture=aic_user_profile.profile_picture,
            )

        return UserProfile(
            id="",
            display_name=DEFAULT_USERNAME,
            profile_picture=self.get_default_avatar(DEFAULT_USERNAME),
        )

    def _encode_data_uri(self, binary_data: bytes, content_type: str | None = None) -> str:
        """
        Encodes binary data to a data URI string.
        """
        base64_encoded_data = base64.b64encode(binary_data).decode("utf-8")
        if content_type:
            return f"data:{content_type};base64,{base64_encoded_data}"
        return base64_encoded_data

    def save_avatar(
        self,
        file,
        file_name: str | None = None,
        content_type: str | None = None,
    ) -> None:
        settings().save(
            PartialSettingsData(user_profile=PartialUserProfile(profile_picture=file.read())),
            to_global=True,
        )

    def get_default_avatar(self, user_id: str) -> str:
        img_filename = self._deterministic_choice(
            blob=user_id,
            choices=list(resource_to_path(resource=DEFAULT_AVATARS_PATH).glob(pattern="*")),
        )
        with open(img_filename, mode="rb") as img:
            file = img.read()
        mime_type, _ = guess_type(img_filename)
        return self._encode_data_uri(file, mime_type)

    def _deterministic_choice(self, blob: str, choices: list[Path]) -> Path:
        hash_value = hashlib.sha256(string=blob.encode()).hexdigest()
        choice_index = int(hash_value, base=16) % len(choices)
        return choices[choice_index]


@lru_cache
def user_profile_service() -> UserProfileService:
    return UserProfileService()
