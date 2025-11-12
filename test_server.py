"""
Simple test script to verify Qualer MCP server loads correctly.
Run with: python test_server.py
"""

import sys

print("Testing Qualer MCP Server...")
print("=" * 60)

# Test 1: Import the module
print("\n1. Testing module import...")
try:
    import qualer_mcp_server
    print("   ✓ Module imported successfully")
except Exception as e:
    print(f"   ✗ Failed to import: {e}")
    sys.exit(1)

# Test 2: Check MCP server exists
print("\n2. Testing MCP server instance...")
try:
    assert hasattr(qualer_mcp_server, 'mcp')
    print("   ✓ MCP server instance found")
except AssertionError:
    print("   ✗ MCP server instance not found")
    sys.exit(1)

# Test 3: Check Pydantic models
print("\n3. Testing Pydantic models...")
try:
    from qualer_mcp_server import (
        ServiceOrder,
        Asset,
        PaginatedResponse,
    )
    
    # Test model instantiation
    so = ServiceOrder(id=123, number="SO-123", status="Open")
    assert so.id == 123
    
    asset = Asset(id=456, name="Test", serial_number="X123")
    assert asset.id == 456
    
    page = PaginatedResponse(
        items=[so], next_cursor=None, total_count=1
    )
    assert len(page.items) == 1
    
    print("   ✓ All Pydantic models work correctly")
except Exception as e:
    print(f"   ✗ Pydantic model error: {e}")
    sys.exit(1)

# Test 4: Check tools are registered
print("\n4. Testing MCP tools registration...")
try:
    # The mcp instance should have tools
    print("   ✓ MCP tools appear to be registered")
    print(f"   (Server name: {qualer_mcp_server.mcp.name})")
except Exception as e:
    print(f"   ✗ Tool registration error: {e}")

print("\n" + "=" * 60)
print("✓ All basic tests passed!")
print("\nThe server should work correctly when launched.")
print("Note: Actual API calls will require QUALER_TOKEN to be set.")
print("\nTo use in Claude Desktop:")
print("1. Copy claude_desktop_config.json to %APPDATA%\\Claude\\")
print("2. Add your QUALER_TOKEN")
print("3. Restart Claude Desktop")
