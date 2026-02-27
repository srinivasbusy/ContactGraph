"""Tests for contact sync endpoints."""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.dependencies import set_neo4j_service


CURRENT_USER = {
    "phone": "+12025550100",
    "email": "alice@example.com",
    "name": "Alice",
    "google_id": "uid-123",
}

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
    mock_service.sync_contacts.return_value = {"synced": 2}
    mock_service.remove_contact.return_value = True
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


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_sync_contacts(client):
    payload = {
        "contacts": [
            {"phone": "+12025550101", "name": "Bob"},
            {"phone": "+12025550102", "name": "Carol"},
        ]
    }
    resp = client.post(
        "/api/v1/contacts/sync",
        json=payload,
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["synced"] == 2
    assert "synced successfully" in data["message"]


def test_sync_contacts_empty_list(client):
    resp = client.post(
        "/api/v1/contacts/sync",
        json={"contacts": []},
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp.status_code == 200


def test_update_contact_add(client, mock_neo4j):
    mock_neo4j.sync_contacts.return_value = {"synced": 1}
    resp = client.put(
        "/api/v1/contacts/update",
        json={"phone": "+12025550101", "name": "Bob", "action": "add"},
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp.status_code == 200
    assert resp.json()["message"] == "Contact added."


def test_update_contact_remove(client):
    resp = client.put(
        "/api/v1/contacts/update",
        json={"phone": "+12025550101", "name": "Bob", "action": "remove"},
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp.status_code == 200
    assert resp.json()["message"] == "Contact removed."


def test_update_contact_invalid_action(client):
    resp = client.put(
        "/api/v1/contacts/update",
        json={"phone": "+12025550101", "name": "Bob", "action": "invalid"},
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp.status_code == 400


def test_delete_contact(client):
    resp = client.delete(
        "/api/v1/contacts/%2B12025550101",
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp.status_code == 200


def test_delete_contact_not_found(client, mock_neo4j):
    mock_neo4j.remove_contact.return_value = False
    resp = client.delete(
        "/api/v1/contacts/%2B12025550199",
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp.status_code == 404


def test_sync_requires_auth(client):
    resp = client.post("/api/v1/contacts/sync", json={"contacts": []})
    assert resp.status_code == 403
