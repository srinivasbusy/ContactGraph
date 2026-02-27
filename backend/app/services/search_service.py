from typing import Dict, Any, List, Optional

from app.services.neo4j_service import Neo4jService
from app.models.search import SearchResponse, NetworkStats, DirectContact
from app.models.user import UserResponse


class SearchService:
    def __init__(self, neo4j: Neo4jService) -> None:
        self._neo4j = neo4j

    def find_connection(
        self, from_phone: str, to_phone: str, max_depth: int = 6
    ) -> SearchResponse:
        """Find the shortest connection path between two users."""
        result = self._neo4j.find_shortest_path(from_phone, to_phone, max_depth)
        if not result:
            return SearchResponse(
                found=False,
                degree=0,
                path=[],
                message="No connection found within the specified depth.",
            )
        path_users = [
            UserResponse(
                phone=node.get("phone", ""),
                name=node.get("name", ""),
                email=node.get("email"),
                is_app_user=node.get("is_app_user", False),
                created_at=node.get("created_at"),
            )
            for node in result["nodes"]
        ]
        degree = result["degree"]
        return SearchResponse(
            found=True,
            degree=degree,
            path=path_users,
            message=f"Connected through {degree} degree(s) of separation.",
        )

    def get_network_stats(self, user_phone: str) -> NetworkStats:
        stats = self._neo4j.get_network_stats(user_phone)
        return NetworkStats(**stats)

    def get_direct_contacts(self, user_phone: str) -> List[DirectContact]:
        contacts = self._neo4j.get_direct_contacts(user_phone)
        return [
            DirectContact(
                phone=c.get("phone", ""),
                name=c.get("name", ""),
                is_app_user=c.get("is_app_user", False),
            )
            for c in contacts
        ]
