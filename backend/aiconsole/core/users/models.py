from typing import Optional

from pydantic import BaseModel, EmailStr, HttpUrl, validator

DEFAULT_USERNAME = "user"


class UserProfile(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar_url: Optional[HttpUrl | str] = None
    gravatar: bool = False

    @validator("username", pre=True, always=True)
    def set_default_username(cls, v: Optional[str], values: dict) -> str:
        if v is None:
            email = values.get("email")
            if isinstance(email, str):
                return email.split("@")[0]
            return DEFAULT_USERNAME
        return v
