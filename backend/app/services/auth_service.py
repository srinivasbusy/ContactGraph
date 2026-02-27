import logging
from typing import Dict, Any

import firebase_admin
from firebase_admin import auth as firebase_auth
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


def verify_firebase_token(id_token: str) -> Dict[str, Any]:
    """
    Verify a Firebase ID token and return the decoded claims.

    Raises HTTPException 401 if the token is invalid or expired.
    """
    try:
        decoded = firebase_auth.verify_id_token(id_token)
        return decoded
    except firebase_auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firebase token has expired.",
        )
    except firebase_auth.InvalidIdTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Firebase token: {exc}",
        )
    except Exception as exc:
        logger.exception("Unexpected error verifying Firebase token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not verify token: {exc}",
        )
