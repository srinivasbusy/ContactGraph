import logging
from typing import Generator, Dict, Any

import firebase_admin
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import settings
from app.services.neo4j_service import Neo4jService
from app.services.auth_service import verify_firebase_token

logger = logging.getLogger(__name__)

# Reusable HTTP Bearer scheme (auto-extracts the token from Authorization header)
_bearer_scheme = HTTPBearer()

# Module-level Neo4j driver singleton (populated at startup by main.py)
_neo4j_service: Neo4jService | None = None


def set_neo4j_service(service: Neo4jService) -> None:
    global _neo4j_service
    _neo4j_service = service


def get_db() -> Generator[Neo4jService, None, None]:
    """Yield the shared Neo4jService instance."""
    if _neo4j_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not initialised.",
        )
    yield _neo4j_service


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    db: Neo4jService = Depends(get_db),
) -> Dict[str, Any]:
    """
    Verify the Firebase ID token and return a user dict.

    The returned dict includes: phone, email, name, google_id.
    """
    decoded = verify_firebase_token(credentials.credentials)

    phone: str = decoded.get("phone_number", "")
    email: str = decoded.get("email", "")
    name: str = decoded.get("name", email.split("@")[0] if email else "Unknown")
    google_id: str = decoded.get("uid", "")

    if not phone and not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token must contain a phone number or email.",
        )

    # Ensure the user exists in the graph
    user = db.get_user_by_phone(phone) if phone else None
    if not user:
        user = db.create_user(
            phone=phone,
            name=name,
            email=email,
            google_id=google_id,
            is_app_user=True,
        )

    return {
        "phone": phone,
        "email": email,
        "name": name,
        "google_id": google_id,
    }
