from pydantic import BaseModel
from typing import List


class ContactData(BaseModel):
    phone: str
    name: str


class ContactSyncRequest(BaseModel):
    contacts: List[ContactData]


class ContactUpdateRequest(BaseModel):
    phone: str
    name: str
    action: str = "add"  # "add" or "remove"
