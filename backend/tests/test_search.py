"""Tests for search and network endpoints."""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.dependencies import set_neo4j_service


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def mock_neo4j():
    mock_service = MagicMock()
    mock_service.get_user_by_phone.return_value = {
        "phone": "+12025550100",
        "name": "Alice",
        "is_app_user": True,
    }
    mock_service.find_shortest_path.return_value = {
        "degree": 2,
        "nodes": [
            {"phone": "+12025550100", "name": "Alice", "is_app_user": True, "email": None, "created_at": None},
            {"phone": "+12025550101", "name": "Bob",   "is_app_user": True, "email": None, "created_at": None},
            {"phone": "+12025550102", "name": "Carol", "is_app_user": True, "email": None, "created_at": None},
        ],
    }
    mock_service.get_network_stats.return_value = {
        "total_contacts": 5,
        "app_users_count": 3,
        "non_app_users_count": 2,
    }
    mock_service.get_direct_contacts.return_value = [
        {"phone": "+12025550101", "name": "Bob",   "is_app_user": True},
        {"phone": "+12025550103", "name": "Dave",  "is_app_user": False},
    ]
    with patch("app.main.Neo4jService", return_value=mock_service):
        set_neo4j_service(mock_service)
        yield mock_service


@pytest.fixture()
def client(mock_neo4j):
    with patch("firebase_admin._apps", {}), \
         patch("firebase_admin.initialize_app"):
        with TestClient(app) as c:
            yield c


@pytest.fixture(autouse=True)
def mock_auth():
    with patch("app.dependencies.verify_firebase_token", return_value={
        "uid": "uid-123",
        "phone_number": "+12025550100",
        "email": "alice@example.com",
        "name": "Alice",
    }):
        yield


AUTH_HEADER = {"Authorization": "Bearer fake-token"}

# ---------------------------------------------------------------------------
# Search tests
# ---------------------------------------------------------------------------

def test_search_found(client):
    resp = client.get("/api/v1/search?phone=%2B12025550102", headers=AUTH_HEADER)
    assert resp.status_code == 200
    data = resp.json()
    assert data["found"] is True
    assert data["degree"] == 2
    assert len(data["path"]) == 3


def test_search_not_found(client, mock_neo4j):
    mock_neo4j.find_shortest_path.return_value = None
    resp = client.get("/api/v1/search?phone=%2B12025559999", headers=AUTH_HEADER)
    assert resp.status_code == 200
    data = resp.json()
    assert data["found"] is False
    assert data["degree"] == 0
    assert data["path"] == []


def test_search_requires_auth(client):
    resp = client.get("/api/v1/search?phone=%2B12025550102")
    assert resp.status_code == 403


def test_search_missing_phone(client):
    resp = client.get("/api/v1/search", headers=AUTH_HEADER)
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Network stats tests
# ---------------------------------------------------------------------------

def test_network_stats(client):
    resp = client.get("/api/v1/network/stats", headers=AUTH_HEADER)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_contacts"] == 5
    assert data["app_users_count"] == 3
    assert data["non_app_users_count"] == 2


# ---------------------------------------------------------------------------
# Direct contacts tests
# ---------------------------------------------------------------------------

def test_direct_contacts(client):
    resp = client.get("/api/v1/network/direct", headers=AUTH_HEADER)
    assert resp.status_code == 200
    contacts = resp.json()
    assert len(contacts) == 2
    phones = {c["phone"] for c in contacts}
    assert "+12025550101" in phones
    assert "+12025550103" in phones


def test_direct_contacts_requires_auth(client):
    resp = client.get("/api/v1/network/direct")
    assert resp.status_code == 403
