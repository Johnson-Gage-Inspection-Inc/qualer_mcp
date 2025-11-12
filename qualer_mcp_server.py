"""
Qualer MCP Server

Production-ready MCP server wrapping the Qualer SDK for AI agent integration.
Exposes Qualer API operations as MCP tools and read-only data as resources.
"""

from __future__ import annotations

import json
import os
from typing import Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from pydantic import Field
from qualer_sdk import AuthenticatedClient
from qualer_sdk.api.assets import get_all_assets
from qualer_sdk.api.assets import get_asset as sdk_get_asset
from qualer_sdk.api.service_order_documents import get_documents_list
from qualer_sdk.api.service_orders import get_work_order, get_work_orders

# Load environment variables from .env file
load_dotenv()


# ============================================================================
# Configuration & Client
# ============================================================================

# Global SDK client
_client: Optional[AuthenticatedClient] = None


def get_client() -> AuthenticatedClient:
    """Get the initialized Qualer SDK client."""
    if _client is None:
        raise RuntimeError("Qualer SDK client not initialized")
    return _client


def set_client(client: AuthenticatedClient) -> None:
    """Set the Qualer SDK client (used for testing)."""
    global _client
    _client = client


def init_client() -> AuthenticatedClient:
    """Initialize the Qualer SDK client with credentials from environment."""
    base_url = os.getenv("QUALER_BASE_URL", "https://jgiquality.qualer.com")
    token = os.getenv("QUALER_TOKEN")

    if not token:
        raise ValueError("QUALER_TOKEN environment variable is required")

    return AuthenticatedClient(
        base_url=base_url,
        token=token,
        raise_on_unexpected_status=True,
    )


# ============================================================================
# MCP Server Instance
# ============================================================================

mcp = FastMCP("Qualer SDK")


# ============================================================================
# MCP Tools
# ============================================================================


@mcp.tool()
def get_service_order(
    so_id: int = Field(description="Service order ID to retrieve"),
) -> dict:
    """
    Fetch a single service order by its ID.

    Returns full details including status, client info, and timestamps.
    Use this when you need current information about a specific SO.
    """
    client = get_client()

    try:
        response = get_work_order.sync_detailed(
            service_order_id=so_id,
            client=client,
        )

        if response.status_code == 404:
            raise ValueError(f"Service order {so_id} not found")

        if response.parsed is None:
            raise ValueError(f"Failed to parse service order {so_id}")

        # Convert SDK model to dict
        return response.parsed.to_dict()

    except ValueError:
        # Re-raise ValueError as-is
        raise
    except Exception as e:
        raise ValueError(
            f"Error fetching service order {so_id}: {str(e)}"
        ) from e


@mcp.tool()
def search_service_orders(
    status: Optional[str] = Field(
        default=None, description="Filter by status (e.g., Open, Closed)"
    ),
    limit: int = Field(
        default=25,
        ge=1,
        le=100,
        description="Maximum items to return (1-100)",
    ),
) -> dict:
    """
    Search service orders with optional filters and pagination.

    Supports filtering by status. Returns paginated results.
    """
    client = get_client()

    try:
        response = get_work_orders.sync_detailed(
            client=client,
            limit=limit,
            status=status,
        )

        if response.parsed is None:
            raise ValueError("Failed to parse service orders")

        return response.parsed.to_dict()

    except ValueError:
        # Re-raise ValueError as-is
        raise
    except Exception as e:
        raise ValueError(
            f"Error searching service orders: {str(e)}"
        ) from e


@mcp.tool()
def get_asset(
    asset_id: int = Field(description="Asset ID to retrieve"),
) -> dict:
    """
    Fetch a single asset/equipment record by its ID.

    Returns full details including serial number, model, manufacturer,
    and location.
    """
    client = get_client()

    try:
        response = sdk_get_asset.sync_detailed(
            asset_id=asset_id,
            client=client,
        )

        if response.status_code == 404:
            raise ValueError(f"Asset {asset_id} not found")

        if response.parsed is None:
            raise ValueError(f"Failed to parse asset {asset_id}")

        return response.parsed.to_dict()

    except ValueError:
        # Re-raise ValueError as-is
        raise
    except Exception as e:
        raise ValueError(
            f"Error fetching asset {asset_id}: {str(e)}"
        ) from e


@mcp.tool()
def search_assets(
    query: Optional[str] = Field(
        default=None,
        description="Search query (name, serial number, model, etc.)",
    ),
    limit: int = Field(
        default=25, ge=1, le=100,
        description="Maximum items to return (1-100)",
    ),
) -> dict:
    """
    Search/list all assets.

    Returns all assets in the system with optional client-side filtering.

    Note: This function fetches ALL assets from the API and filters
    client-side. For systems with large asset counts, this may be
    memory-intensive. Consider API pagination improvements for production use.
    """
    client = get_client()

    try:
        response = get_all_assets.sync_detailed(client=client)

        if response.parsed is None:
            raise ValueError("Failed to parse assets")

        # Convert list of SDK models to list of dicts
        assets = [asset.to_dict() for asset in response.parsed]

        # If query provided, filter results client-side
        if query:
            query_lower = query.lower()

            def matches_query(asset: dict) -> bool:
                name = asset.get("name")
                serial = asset.get("serial_number")
                model = asset.get("model")
                return bool(
                    (name and query_lower in str(name).lower())
                    or (serial and query_lower in str(serial).lower())
                    or (model and query_lower in str(model).lower())
                )

            assets = [a for a in assets if matches_query(a)]

        # Apply limit
        return {"items": assets[:limit], "total": len(assets)}

    except ValueError:
        # Re-raise ValueError as-is
        raise
    except Exception as e:
        raise ValueError(
            f"Error searching assets: {str(e)}"
        ) from e


@mcp.tool()
def list_service_order_documents(
    so_id: int = Field(description="Service order ID to list documents for"),
) -> dict:
    """
    List all documents attached to a service order.

    Returns metadata for each document (filename, upload time, size).
    """
    client = get_client()

    try:
        response = get_documents_list.sync_detailed(
            service_order_id=so_id,
            client=client,
        )

        if response.status_code == 404:
            raise ValueError(f"Service order {so_id} not found")

        if response.parsed is None:
            msg = f"Failed to parse documents for service order {so_id}"
            raise ValueError(msg)

        # Convert list of SDK models to list of dicts
        docs = [doc.to_dict() for doc in response.parsed]
        return {"service_order_id": so_id, "documents": docs}

    except ValueError:
        # Re-raise ValueError as-is
        raise
    except Exception as e:
        msg = f"Error fetching documents for SO {so_id}: {str(e)}"
        raise ValueError(msg) from e


# ============================================================================
# MCP Resources
# ============================================================================


@mcp.resource("qualer://service-order/{so_id}")
def service_order_resource(so_id: int) -> str:
    """
    Read-only view of a service order as formatted JSON.

    Use this resource when you need to load service order context
    without making a direct API call. Ideal for agent reasoning tasks.
    """
    so = get_service_order(so_id)
    return json.dumps(so, indent=2)


@mcp.resource("qualer://asset/{asset_id}")
def asset_resource(asset_id: int) -> str:
    """
    Read-only view of an asset as formatted JSON.

    Use this resource when you need to load asset/equipment context
    without making a direct API call. Ideal for agent reasoning tasks.
    """
    asset = get_asset(asset_id)
    return json.dumps(asset, indent=2)


# ============================================================================
# Server Entrypoint
# ============================================================================


def main():
    """Launch MCP server over stdio transport."""
    global _client

    # Initialize SDK client
    _client = init_client()

    # Run the MCP server
    mcp.run()


if __name__ == "__main__":
    # CRITICAL: Never print to stdout on stdio transport
    main()
