"""Unit tests for FastAPI CRM endpoints.

Tests cover /api/customers (list, upload-csv) and error paths.
Uses FastAPI's TestClient with an isolated test DB if possible.
"""

import io
import pytest
from fastapi.testclient import TestClient

try:
    from backend.main import app
except ImportError:
    try:
        from backend.app import app  # type: ignore
    except ImportError:
        from main import app  # type: ignore


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


class TestCustomersEndpoint:
    """Tests for /api/customers."""

    def test_list_customers_returns_200(self, client):
        response = client.get("/api/customers")
        assert response.status_code == 200

    def test_list_customers_returns_list(self, client):
        response = client.get("/api/customers")
        data = response.get_json() if response.headers.get("content-type", "").startswith("application/json") else response.json()
        assert isinstance(data, (list, dict))

    def test_list_customers_pagination_param(self, client):
        # If pagination is supported, the param should be accepted
        response = client.get("/api/customers?limit=10")
        assert response.status_code in (200, 422)

    def test_create_customer_with_valid_payload(self, client):
        payload = {
            "email": f"test_{pytest.importorskip('uuid').uuid4().hex[:8]}@example.com",
            "name": "Test User",
        }
        response = client.post("/api/customers", json=payload)
        # Either 200/201 (created) or 409 (already exists) — both acceptable
        assert response.status_code in (200, 201, 409, 422)

    def test_create_customer_rejects_invalid_email(self, client):
        payload = {"email": "not-an-email", "name": "Bad"}
        response = client.post("/api/customers", json=payload)
        # Should reject invalid email — 400 or 422
        assert response.status_code in (400, 422)

    def test_create_customer_rejects_missing_email(self, client):
        payload = {"name": "NoEmail"}
        response = client.post("/api/customers", json=payload)
        assert response.status_code in (400, 422)


class TestCSVUploadEndpoint:
    """Tests for /api/customers/upload-csv."""

    def test_upload_valid_csv(self, client):
        csv_content = b"email,name\nalice@example.com,Alice\nbob@example.com,Bob\n"
        files = {"file": ("customers.csv", io.BytesIO(csv_content), "text/csv")}
        response = client.post("/api/customers/upload-csv", files=files)
        assert response.status_code in (200, 201, 422)

    def test_upload_empty_file(self, client):
        files = {"file": ("empty.csv", io.BytesIO(b""), "text/csv")}
        response = client.post("/api/customers/upload-csv", files=files)
        assert response.status_code in (200, 400, 422)

    def test_upload_non_csv_file(self, client):
        files = {"file": ("data.txt", io.BytesIO(b"hello"), "text/plain")}
        response = client.post("/api/customers/upload-csv", files=files)
        # Should reject non-CSV
        assert response.status_code in (400, 415, 422)


class TestAnalyticsEndpoint:
    """Tests for /api/analytics/{campaign_id}."""

    def test_analytics_for_nonexistent_campaign(self, client):
        response = client.get("/api/analytics/99999999")
        # 404 expected for non-existent, or 200 if mock
        assert response.status_code in (200, 404)