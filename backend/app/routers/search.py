import logging
from typing import Dict, Any

from fastapi import APIRouter, Depends, Request

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.dependencies import get_db, get_current_user
from app.models.search import SearchResponse
from app.services.search_service import SearchService
from app.services.neo4j_service import Neo4jService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/search", tags=["search"])
limiter = Limiter(key_func=get_remote_address)


@router.get("", response_model=SearchResponse)
@limiter.limit("30/minute")
async def find_connection(
    request: Request,
    phone: str,
    max_depth: int = 6,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Neo4jService = Depends(get_db),
) -> SearchResponse:
    """Find the shortest connection chain between the current user and *phone*."""
    service = SearchService(db)
    return service.find_connection(current_user["phone"], phone, max_depth)
