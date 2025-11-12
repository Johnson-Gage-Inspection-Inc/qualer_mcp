"""
Quick test to verify the server can make actual API calls.
"""

import qualer_mcp_server
from qualer_mcp_server import get_service_order, init_client


def test_get_service_order():
    """Test fetching a specific service order."""
    print("Testing get_service_order with ID 1188722...")
    print("=" * 60)

    try:
        # Initialize the client
        qualer_mcp_server._client = init_client()

        # Fetch the service order
        result = get_service_order(1188722)

        print("✓ Successfully retrieved service order!")
        print("\nService Order Details:")
        print(f"  ID: {result.get('ServiceOrderId')}")
        print(f"  Number: {result.get('ServiceOrderNumber')}")
        print(f"  Status: {result.get('OrderStatus')}")
        print(f"  Customer: {result.get('ClientCompanyName')}")
        print(f"  Location: {result.get('ClientSite')}")
        print(f"  Created: {result.get('CreatedOn')}")

        # Show full JSON
        print(f"\n{'-' * 60}")
        print("Full JSON Response:")
        print(f"{'-' * 60}")
        import json

        print(json.dumps(result, indent=2))

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        print(f"\nError type: {type(e).__name__}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_get_service_order()
    exit(0 if success else 1)
