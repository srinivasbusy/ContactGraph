from typing import Dict, Any, List, Optional

from app.services.neo4j_service import Neo4jService
from app.utils.phone_utils import normalize_phone


class ContactService:
    def __init__(self, neo4j: Neo4jService) -> None:
        self._neo4j = neo4j

    def sync(self, user_phone: str, contacts: List[Dict[str, str]]) -> Dict[str, int]:
        """Bulk-sync contacts and return sync counts."""
        return self._neo4j.sync_contacts(user_phone, contacts)

    def add_contact(self, user_phone: str, contact_phone: str, contact_name: str) -> Dict[str, int]:
        """Add a single contact relationship."""
        return self._neo4j.sync_contacts(
            user_phone, [{"phone": contact_phone, "name": contact_name}]
        )

    def remove_contact(self, user_phone: str, contact_phone: str) -> bool:
        """Remove a single KNOWS relationship."""
        return self._neo4j.remove_contact(user_phone, contact_phone)
