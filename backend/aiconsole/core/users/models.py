from typing import Optional

from pydantic import BaseModel, EmailStr, HttpUrl, model_validator

DEFAULT_USERNAME = "user"


class PartialUserProfile(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar_url: Optional[HttpUrl | str] = None
    gravatar: Optional[bool] = None


class UserProfile(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar_url: Optional[HttpUrl | str] = None
    gravatar: bool = False

    @model_validator(mode="after")
    def set_default_username(self):
        if self.username is None:
            email = self.email
            if email:
                self.username = email.split("@")[0]
            else:
                self.username = DEFAULT_USERNAME
        return self
