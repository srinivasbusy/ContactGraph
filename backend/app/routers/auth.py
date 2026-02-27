import logging
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.dependencies import get_db
from app.services.auth_service import verify_firebase_token
from app.services.neo4j_service import Neo4jService
from app.config import settings
from fastapi import Depends

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class GoogleAuthRequest(BaseModel):
    id_token: str


@router.post("/google")
async def google_auth(
    body: GoogleAuthRequest,
    db: Neo4jService = Depends(get_db),
) -> Dict[str, Any]:
    """
    Verify a Firebase ID token, create or update the user in Neo4j,
    and return the user data.
    """
    decoded = verify_firebase_token(body.id_token)

    phone: str = decoded.get("phone_number", "")
    email: str = decoded.get("email", "")
    name: str = decoded.get("name", email.split("@")[0] if email else "Unknown")
    google_id: str = decoded.get("uid", "")

    if not phone and not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token must contain a phone number or email.",
        )

    user = db.create_user(
        phone=phone,
        name=name,
        email=email,
        google_id=google_id,
        is_app_user=True,
    )

    return {
        "user": user,
        "message": "Authentication successful.",
    }
