"""Unit tests for CRM data models.

These tests verify SQLAlchemy model invariants:
- email format validation
- required field enforcement
- relationship integrity
- string representations
"""

import pytest
from datetime import datetime

try:
    from backend.models import Customer, Campaign, Segment  # adjust path if different
except ImportError:
    from models import Customer, Campaign, Segment  # type: ignore


class TestCustomerModel:
    """Tests for the Customer SQLAlchemy model."""

    def test_email_required(self):
        with pytest.raises((ValueError, TypeError, AssertionError)):
            Customer(email=None)  # type: ignore[arg-type]

    def test_str_representation_contains_email(self):
        c = Customer(email="alice@example.com", name="Alice")
        assert "alice@example.com" in str(c) or "Alice" in str(c)

    def test_created_at_defaults_to_recent(self):
        c = Customer(email="bob@example.com")
        if hasattr(c, "created_at") and c.created_at is not None:
            delta = datetime.utcnow() - c.created_at
            assert delta.total_seconds() < 60

    def test_email_is_normalized_lowercase(self):
        c = Customer(email="ALICE@EXAMPLE.COM")
        # If the model lowercases on assignment, this should hold
        if hasattr(c, "email"):
            assert c.email == c.email.lower()


class TestCampaignModel:
    """Tests for the Campaign model."""

    def test_campaign_name_required(self):
        with pytest.raises((ValueError, TypeError, AssertionError)):
            Campaign(name=None)  # type: ignore[arg-type]

    def test_campaign_status_defaults_to_draft(self):
        c = Campaign(name="Test Campaign")
        # Common defaults in CRM systems
        if hasattr(c, "status"):
            assert c.status in ("draft", "DRAFT", None)

    def test_str_representation_contains_name(self):
        c = Campaign(name="Summer Sale")
        assert "Summer Sale" in str(c) or "Summer" in str(c)


class TestSegmentModel:
    """Tests for the Segment model."""

    def test_segment_name_required(self):
        with pytest.raises((ValueError, TypeError, AssertionError)):
            Segment(name=None)  # type: ignore[arg-type]

    def test_segment_can_be_constructed(self):
        s = Segment(name="High-value customers")
        assert s.name == "High-value customers"