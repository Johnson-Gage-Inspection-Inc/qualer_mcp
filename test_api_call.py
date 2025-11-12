"""
Quick test to verify the server can make actual API calls.
"""
import asyncio
from qualer_mcp_server import get_service_order


async def test_get_service_order():
    """Test fetching a specific service order."""
    print("Testing get_service_order with ID 1188722...")
    print("=" * 60)
    
    try:
        # Initialize the client
        from qualer_mcp_server import init_client
        global _client
        import qualer_mcp_server
        qualer_mcp_server._client = await init_client()
        
        # Fetch the service order
        result = await get_service_order(1188722)
        
        print(f"✓ Successfully retrieved service order!")
        print(f"\nService Order Details:")
        print(f"  ID: {result.id}")
        print(f"  Number: {result.number}")
        print(f"  Status: {result.status}")
        print(f"  Customer: {result.customer_name}")
        print(f"  Asset: {result.asset_name}")
        print(f"  Location: {result.location}")
        print(f"  Created: {result.created_at}")
        
        # Show full JSON
        print(f"\n{'-' * 60}")
        print("Full JSON Response:")
        print(f"{'-' * 60}")
        print(result.model_dump_json(indent=2))
        
        # Clean up
        from qualer_mcp_server import close_client
        await close_client(qualer_mcp_server._client)
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print(f"\nError type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_get_service_order())
    exit(0 if success else 1)
