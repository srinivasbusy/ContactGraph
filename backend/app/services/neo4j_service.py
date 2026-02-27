import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

from neo4j import GraphDatabase, Driver
from neo4j.exceptions import Neo4jError

from app.utils.phone_utils import normalize_phone

logger = logging.getLogger(__name__)


class Neo4jService:
    def __init__(self, uri: str, username: str, password: str) -> None:
        self._driver: Driver = GraphDatabase.driver(uri, auth=(username, password))

    def close(self) -> None:
        self._driver.close()

    def verify_connectivity(self) -> None:
        self._driver.verify_connectivity()

    # ------------------------------------------------------------------
    # Schema / indexes
    # ------------------------------------------------------------------

    def create_indexes(self) -> None:
        """Create indexes and constraints on first startup."""
        with self._driver.session() as session:
            session.run(
                "CREATE CONSTRAINT user_phone_unique IF NOT EXISTS "
                "FOR (u:User) REQUIRE u.phone IS UNIQUE"
            )
            session.run(
                "CREATE INDEX user_phone_index IF NOT EXISTS "
                "FOR (u:User) ON (u.phone)"
            )
            logger.info("Neo4j indexes/constraints ensured.")

    # ------------------------------------------------------------------
    # User CRUD
    # ------------------------------------------------------------------

    def create_user(
        self,
        phone: str,
        name: str,
        email: Optional[str] = None,
        google_id: Optional[str] = None,
        is_app_user: bool = True,
    ) -> Dict[str, Any]:
        """MERGE a User node and return its properties."""
        phone = normalize_phone(phone)
        now = datetime.now(timezone.utc).isoformat()
        with self._driver.session() as session:
            result = session.run(
                """
                MERGE (u:User {phone: $phone})
                ON CREATE SET
                    u.name        = $name,
                    u.email       = $email,
                    u.google_id   = $google_id,
                    u.is_app_user = $is_app_user,
                    u.created_at  = $now
                ON MATCH SET
                    u.name        = $name,
                    u.email       = CASE WHEN $email IS NOT NULL THEN $email ELSE u.email END,
                    u.google_id   = CASE WHEN $google_id IS NOT NULL THEN $google_id ELSE u.google_id END,
                    u.is_app_user = CASE WHEN $is_app_user THEN true ELSE u.is_app_user END
                RETURN u
                """,
                phone=phone,
                name=name,
                email=email,
                google_id=google_id,
                is_app_user=is_app_user,
                now=now,
            )
            record = result.single()
            if record:
                return dict(record["u"])
            return {}

    def get_user_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        phone = normalize_phone(phone)
        with self._driver.session() as session:
            result = session.run(
                "MATCH (u:User {phone: $phone}) RETURN u",
                phone=phone,
            )
            record = result.single()
            return dict(record["u"]) if record else None

    # ------------------------------------------------------------------
    # Contacts
    # ------------------------------------------------------------------

    def sync_contacts(self, user_phone: str, contacts: List[Dict[str, str]]) -> Dict[str, int]:
        """
        Bulk-sync a list of contacts for *user_phone*.

        Each contact dict must have keys ``phone`` and ``name``.
        Creates missing User nodes (is_app_user=false) and KNOWS edges.
        Returns counts of created/merged nodes and relationships.
        """
        user_phone = normalize_phone(user_phone)
        normalized: List[Dict[str, str]] = []
        for c in contacts:
            n_phone = normalize_phone(c["phone"])
            normalized.append({"phone": n_phone, "name": c.get("name", "")})

        with self._driver.session() as session:
            result = session.run(
                """
                UNWIND $contacts AS contact
                MERGE (c:User {phone: contact.phone})
                ON CREATE SET
                    c.name        = contact.name,
                    c.is_app_user = false,
                    c.created_at  = $now
                ON MATCH SET
                    c.name = CASE WHEN c.is_app_user = false THEN contact.name ELSE c.name END
                WITH c
                MATCH (u:User {phone: $user_phone})
                MERGE (u)-[:KNOWS]->(c)
                RETURN count(c) AS synced
                """,
                contacts=normalized,
                user_phone=user_phone,
                now=datetime.now(timezone.utc).isoformat(),
            )
            record = result.single()
            return {"synced": record["synced"] if record else 0}

    def remove_contact(self, user_phone: str, contact_phone: str) -> bool:
        user_phone = normalize_phone(user_phone)
        contact_phone = normalize_phone(contact_phone)
        with self._driver.session() as session:
            result = session.run(
                """
                MATCH (u:User {phone: $user_phone})-[r:KNOWS]->(c:User {phone: $contact_phone})
                DELETE r
                RETURN count(r) AS removed
                """,
                user_phone=user_phone,
                contact_phone=contact_phone,
            )
            record = result.single()
            return bool(record and record["removed"] > 0)

    # ------------------------------------------------------------------
    # Graph queries
    # ------------------------------------------------------------------

    def find_shortest_path(
        self, from_phone: str, to_phone: str, max_depth: int = 6
    ) -> Optional[Dict[str, Any]]:
        """Return shortest path info or None if no path exists."""
        from_phone = normalize_phone(from_phone)
        to_phone = normalize_phone(to_phone)
        with self._driver.session() as session:
            result = session.run(
                f"""
                MATCH path = shortestPath(
                    (a:User {{phone: $from_phone}})-[:KNOWS*1..{max_depth}]-(b:User {{phone: $to_phone}})
                )
                RETURN path, length(path) AS degree
                """,
                from_phone=from_phone,
                to_phone=to_phone,
            )
            record = result.single()
            if not record:
                return None
            nodes = [dict(n) for n in record["path"].nodes]
            return {"degree": record["degree"], "nodes": nodes}

    def get_direct_contacts(self, user_phone: str) -> List[Dict[str, Any]]:
        user_phone = normalize_phone(user_phone)
        with self._driver.session() as session:
            result = session.run(
                """
                MATCH (u:User {phone: $user_phone})-[:KNOWS]->(c:User)
                RETURN c
                ORDER BY c.name
                """,
                user_phone=user_phone,
            )
            return [dict(record["c"]) for record in result]

    def get_network_stats(self, user_phone: str) -> Dict[str, int]:
        user_phone = normalize_phone(user_phone)
        with self._driver.session() as session:
            result = session.run(
                """
                MATCH (u:User {phone: $user_phone})-[:KNOWS]->(c:User)
                RETURN
                    count(c) AS total_contacts,
                    sum(CASE WHEN c.is_app_user = true  THEN 1 ELSE 0 END) AS app_users_count,
                    sum(CASE WHEN c.is_app_user = false THEN 1 ELSE 0 END) AS non_app_users_count
                """,
                user_phone=user_phone,
            )
            record = result.single()
            if record:
                return {
                    "total_contacts": record["total_contacts"],
                    "app_users_count": record["app_users_count"],
                    "non_app_users_count": record["non_app_users_count"],
                }
            return {"total_contacts": 0, "app_users_count": 0, "non_app_users_count": 0}
