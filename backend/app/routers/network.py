import logging
from typing import Dict, Any, List

from fastapi import APIRouter, Depends

from app.dependencies import get_db, get_current_user
from app.models.search import NetworkStats, DirectContact
from app.services.search_service import SearchService
from app.services.neo4j_service import Neo4jService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/network", tags=["network"])


@router.get("/stats", response_model=NetworkStats)
async def network_stats(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Neo4jService = Depends(get_db),
) -> NetworkStats:
    """Return contact statistics for the current user."""
    service = SearchService(db)
    return service.get_network_stats(current_user["phone"])


@router.get("/direct", response_model=List[DirectContact])
async def direct_contacts(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Neo4jService = Depends(get_db),
) -> List[DirectContact]:
    """Return all direct (1st-degree) contacts of the current user."""
    service = SearchService(db)
    return service.get_direct_contacts(current_user["phone"])
