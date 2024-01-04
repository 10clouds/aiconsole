from typing import Optional

from pydantic import BaseModel


class UserProfile(BaseModel):
    username: Optional[str]
    email: Optional[str]
    avatar_url: Optional[str]
    gravatar: Optional[bool]
