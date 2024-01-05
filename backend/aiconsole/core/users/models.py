from pydantic import BaseModel, HttpUrl


class UserProfile(BaseModel):
    username: str
    email: str | None
    avatar_url: str | HttpUrl | None
    gravatar: bool
