from datetime import datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl


class Photo(BaseModel):
    value: HttpUrl
    type: str


class ProfileBackground(BaseModel):
    color: str
    url: HttpUrl


class URLItem(BaseModel):
    value: HttpUrl
    title: str


class ShareFlags(BaseModel):
    search_engines: Optional[bool]


class GravatarUserProfile(BaseModel):
    hash: str
    requestHash: str
    profileUrl: HttpUrl
    preferredUsername: str
    thumbnailUrl: HttpUrl
    photos: list[Photo]
    last_profile_edit: datetime | None = None
    profileBackground: Optional[ProfileBackground] = None
    displayName: str
    aboutMe: Optional[str] = None
    currentLocation: Optional[str] = None
    urls: Optional[list[URLItem]] = []
    share_flags: ShareFlags
