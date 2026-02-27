from pydantic import BaseModel
from typing import List, Optional
from app.models.user import UserResponse


class SearchResponse(BaseModel):
    found: bool
    degree: int
    path: List[UserResponse]
    message: str


class NetworkStats(BaseModel):
    total_contacts: int
    app_users_count: int
    non_app_users_count: int


class DirectContact(BaseModel):
    phone: str
    name: str
    is_app_user: bool
