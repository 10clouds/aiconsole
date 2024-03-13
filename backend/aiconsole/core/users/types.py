from pydantic import BaseModel


class PartialUserProfile(BaseModel):
    id: str | None = None
    display_name: str | None = None
    profile_picture: str | None = None


class UserProfile(BaseModel):
    id: str | None = None
    display_name: str | None = None
    profile_picture: str | None = None
