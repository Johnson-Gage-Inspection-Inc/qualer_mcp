"""
Integration tests to verify actual API calls work.

These tests require a valid QUALER_TOKEN environment variable.
Run with: pytest tests/test_api_call.py -v
"""

import pytest

import qualer_mcp_server
from qualer_mcp_server import get_service_order, init_client


@pytest.fixture
def qualer_client():
    """Initialize the Qualer SDK client."""
    client = init_client()
    qualer_mcp_server._client = client
    return client


def test_init_client(qualer_client):
    """Test that the Qualer SDK client initializes successfully."""
    assert qualer_client is not None


def test_get_service_order_valid(qualer_client):
    """Test fetching a valid service order.
    
    Note: This test uses a known service order ID.
    Update 1175961 if this ID is no longer valid in your test environment.
    """
    try:
        result = get_service_order(1175961)
        
        # Verify it's a dict with expected fields
        assert isinstance(result, dict)
        assert "ServiceOrderId" in result
        assert result["ServiceOrderId"] == 1175961
        assert "ServiceOrderNumber" in result
        assert "OrderStatus" in result
        
    except ValueError as e:
        pytest.skip(f"Service order not available in test environment: {e}")


def test_service_order_response_format(qualer_client):
    """Test that service order response has expected structure."""
    try:
        result = get_service_order(1175961)
        
        # Check important fields
        required_fields = [
            "ServiceOrderId",
            "ClientCompanyName",
            "OrderStatus",
            "CreatedOn",
        ]
        for field in required_fields:
            assert field in result, f"Missing field: {field}"
            
    except ValueError:
        pytest.skip("Service order not available in test environment")
