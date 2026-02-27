from pydantic import BaseModel
from typing import Optional


class UserCreate(BaseModel):
    phone: str
    name: str
    email: Optional[str] = None
    google_id: Optional[str] = None


class UserResponse(BaseModel):
    phone: str
    name: str
    email: Optional[str] = None
    is_app_user: bool = True
    created_at: Optional[str] = None
