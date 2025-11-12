"""
Basic tests for Qualer MCP Server

Run with: pytest test_qualer_mcp.py
"""

from qualer_mcp_server import ServiceOrder, Asset, PaginatedResponse


def test_service_order_model():
    """Test ServiceOrder Pydantic model."""
    so = ServiceOrder(
        id=123,
        number="SO-12345",
        status="Open",
        client_company_id=42,
    )
    assert so.id == 123
    assert so.number == "SO-12345"
    assert so.status == "Open"


def test_asset_model():
    """Test Asset Pydantic model."""
    asset = Asset(
        id=456,
        name="Test Equipment",
        serial_number="X123",
        manufacturer="ACME Corp",
    )
    assert asset.id == 456
    assert asset.name == "Test Equipment"
    assert asset.serial_number == "X123"


def test_paginated_response():
    """Test PaginatedResponse model."""
    items = [
        ServiceOrder(id=1, number="SO-1", status="Open"),
        ServiceOrder(id=2, number="SO-2", status="Closed"),
    ]
    page = PaginatedResponse(
        items=items, next_cursor="cursor123", total_count=10
    )
    assert len(page.items) == 2
    assert page.next_cursor == "cursor123"
    assert page.total_count == 10


def test_service_order_json_serialization():
    """Test JSON serialization of models."""
    so = ServiceOrder(
        id=789, number="SO-789", status="In Progress"
    )
    json_str = so.model_dump_json()
    assert '"id": 789' in json_str or '"id":789' in json_str
    assert "SO-789" in json_str


# Integration tests would require a mock Qualer API or test environment
# For now, these basic model tests ensure schema correctness
