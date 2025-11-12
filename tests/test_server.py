"""
Tests to verify Qualer MCP server loads correctly.

Run with: pytest tests/test_server.py -v
"""

import qualer_mcp_server


def test_module_import():
    """Test that the qualer_mcp_server module imports successfully."""
    assert qualer_mcp_server is not None


def test_mcp_server_instance():
    """Test that the MCP server instance exists."""
    assert hasattr(qualer_mcp_server, "mcp")
    assert qualer_mcp_server.mcp is not None


def test_mcp_server_name():
    """Test that the MCP server has the correct name."""
    assert qualer_mcp_server.mcp.name == "Qualer SDK"


def test_tools_registered():
    """Test that MCP tools are registered."""
    # Check that get_client function exists
    assert hasattr(qualer_mcp_server, "get_client")
    assert callable(qualer_mcp_server.get_client)


def test_init_client_function():
    """Test that init_client function exists."""
    assert hasattr(qualer_mcp_server, "init_client")
    assert callable(qualer_mcp_server.init_client)


def test_tool_functions_exist():
    """Test that all expected tool functions exist."""
    tools = [
        "get_service_order",
        "search_service_orders",
        "get_asset",
        "search_assets",
        "list_service_order_documents",
    ]
    for tool_name in tools:
        assert hasattr(qualer_mcp_server, tool_name)
        assert callable(getattr(qualer_mcp_server, tool_name))
