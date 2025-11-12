"""
Basic tests for Qualer MCP Server

Run with: pytest tests/test_qualer_mcp.py -v
"""

import qualer_mcp_server


def test_server_initialization():
    """Test that the server initializes without errors."""
    assert qualer_mcp_server.mcp is not None
    assert qualer_mcp_server.mcp.name == "Qualer SDK"


def test_get_client_function_exists():
    """Test that get_client function is defined."""
    assert hasattr(qualer_mcp_server, "get_client")
    assert callable(qualer_mcp_server.get_client)


def test_init_client_function_exists():
    """Test that init_client function is defined."""
    assert hasattr(qualer_mcp_server, "init_client")
    assert callable(qualer_mcp_server.init_client)


def test_service_order_tool_exists():
    """Test that get_service_order tool is defined."""
    assert hasattr(qualer_mcp_server, "get_service_order")
    assert callable(qualer_mcp_server.get_service_order)


def test_search_service_orders_tool_exists():
    """Test that search_service_orders tool is defined."""
    assert hasattr(qualer_mcp_server, "search_service_orders")
    assert callable(qualer_mcp_server.search_service_orders)


def test_asset_tool_exists():
    """Test that get_asset tool is defined."""
    assert hasattr(qualer_mcp_server, "get_asset")
    assert callable(qualer_mcp_server.get_asset)


def test_search_assets_tool_exists():
    """Test that search_assets tool is defined."""
    assert hasattr(qualer_mcp_server, "search_assets")
    assert callable(qualer_mcp_server.search_assets)


def test_list_documents_tool_exists():
    """Test that list_service_order_documents tool is defined."""
    assert hasattr(qualer_mcp_server, "list_service_order_documents")
    assert callable(qualer_mcp_server.list_service_order_documents)
