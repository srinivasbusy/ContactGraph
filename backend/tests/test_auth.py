"""Tests for authentication endpoints."""
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
    """Inject a mock Neo4jService for every test, preventing real Neo4j connections."""
    mock_service = MagicMock()
    mock_service.get_user_by_phone.return_value = None
    mock_service.create_user.return_value = {
        "phone": "+12025550100",
        "name": "Alice",
        "email": "alice@example.com",
        "is_app_user": True,
        "created_at": "2024-01-01T00:00:00+00:00",
    }
    with patch("app.main.Neo4jService", return_value=mock_service):
        set_neo4j_service(mock_service)
        yield mock_service


@pytest.fixture()
def client(mock_neo4j):
    with patch("firebase_admin._apps", {}), \
         patch("firebase_admin.initialize_app"):
        with TestClient(app) as c:
            yield c


DECODED_TOKEN = {
    "uid": "google-uid-123",
    "phone_number": "+12025550100",
    "email": "alice@example.com",
    "name": "Alice",
}

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_health_check(client):
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_google_auth_success(client):
    with patch(
        "app.routers.auth.verify_firebase_token", return_value=DECODED_TOKEN
    ):
        resp = client.post("/api/v1/auth/google", json={"id_token": "valid-token"})

    assert resp.status_code == 200
    data = resp.json()
    assert data["message"] == "Authentication successful."
    assert data["user"]["phone"] == "+12025550100"


def test_google_auth_invalid_token(client):
    from fastapi import HTTPException

    with patch(
        "app.routers.auth.verify_firebase_token",
        side_effect=HTTPException(status_code=401, detail="Invalid Firebase token"),
    ):
        resp = client.post("/api/v1/auth/google", json={"id_token": "bad-token"})

    assert resp.status_code == 401


def test_google_auth_missing_body(client):
    resp = client.post("/api/v1/auth/google", json={})
    assert resp.status_code == 422
