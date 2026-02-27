import logging
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Request, status

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.dependencies import get_db, get_current_user
from app.models.contact import ContactSyncRequest, ContactUpdateRequest
from app.services.contact_service import ContactService
from app.services.neo4j_service import Neo4jService
from app.utils.phone_utils import normalize_phone

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/contacts", tags=["contacts"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/sync")
@limiter.limit("5/minute")
async def sync_contacts(
    request: Request,
    body: ContactSyncRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Neo4jService = Depends(get_db),
) -> Dict[str, Any]:
    """Bulk-sync the caller's contact list."""
    service = ContactService(db)
    contacts = [{"phone": c.phone, "name": c.name} for c in body.contacts]
    result = service.sync(current_user["phone"], contacts)
    return {"message": "Contacts synced successfully.", **result}


@router.put("/update")
async def update_contact(
    body: ContactUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Neo4jService = Depends(get_db),
) -> Dict[str, Any]:
    """Add or remove a single contact."""
    service = ContactService(db)
    if body.action == "add":
        result = service.add_contact(current_user["phone"], body.phone, body.name)
        return {"message": "Contact added.", **result}
    elif body.action == "remove":
        removed = service.remove_contact(current_user["phone"], normalize_phone(body.phone))
        if not removed:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact relationship not found.",
            )
        return {"message": "Contact removed."}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="action must be 'add' or 'remove'.",
        )


@router.delete("/{phone}")
async def delete_contact(
    phone: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Neo4jService = Depends(get_db),
) -> Dict[str, Any]:
    """Remove a contact relationship by phone number."""
    service = ContactService(db)
    removed = service.remove_contact(current_user["phone"], phone)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact relationship not found.",
        )
    return {"message": "Contact removed."}
