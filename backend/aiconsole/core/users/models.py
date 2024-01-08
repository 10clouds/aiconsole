from pydantic import BaseModel, HttpUrl

DEFAULT_USERNAME = "user"


class UserProfile(BaseModel):
    username: str
    email: str | None = None
    avatar_url: str | HttpUrl | None = None
    gravatar: bool = False

    def __init__(self, **data):
        if "email" in data and data["email"] is not None:
            data["username"] = str(data["email"]).split("@")[0]
        else:
            data["username"] = DEFAULT_USERNAME
        super().__init__(**data)
