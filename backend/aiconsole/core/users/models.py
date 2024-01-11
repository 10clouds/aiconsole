from typing import Any

from pydantic import BaseModel, EmailStr, HttpUrl

DEFAULT_USERNAME = "user"


class UserProfile(BaseModel):
    username: str
    email: EmailStr | None = None
    avatar_url: str | HttpUrl | None = None
    gravatar: bool = False

    def __init__(self, **data: Any):
        if data.get("username") is None:
            if data.get("email") is not None:
                data["username"] = str(data["email"]).split("@")[0]
            else:
                data["username"] = DEFAULT_USERNAME
        super().__init__(**data)
