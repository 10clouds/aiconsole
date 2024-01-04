import hashlib

from aiconsole.core.users.models import UserProfile

import requests


class GravatarProfileService:
    @staticmethod
    def get_gravatar_profile(email: str) -> UserProfile | None:
        gravatar_url = f"https://www.gravatar.com/{hashlib.md5(email.lower().encode()).hexdigest()}.json"
        try:
            response = requests.get(gravatar_url)
            response.raise_for_status()
            gravatar_data = response.json()
            entry = gravatar_data["entry"][0]
            return UserProfile(
                username=entry.get("preferredUsername", email),
                email=email,
                avatar_url=entry.get("thumbnailUrl", ""),
                gravatar=True,
            )
        except requests.RequestException:
            return None
