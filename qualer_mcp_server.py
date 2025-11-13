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
from qualer_sdk.api.assets import get_asset_manager_list
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
        raise ValueError(f"Error fetching service order {so_id}: {str(e)}") from e


@mcp.tool()
def search_service_orders(
    status: Optional[str] = Field(
        default=None, description="Filter by status (e.g., Open, Closed)"
    ),
    company_id: Optional[int] = Field(
        default=None, description="Filter by client company ID"
    ),
    work_order_number: Optional[str] = Field(
        default=None, description="Filter by work order number"
    ),
    assigned_employees: Optional[str] = Field(
        default=None, description="Filter by assigned employee names"
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

    Supports filtering by status, company, work order number, and assigned
    employees. Returns paginated results.

    Note: The underlying API does not support server-side pagination. Results
    are fetched from the API and limited client-side. The 'total' field
    reflects the number of records returned from the API after filtering,
    not the total count of all matching records in the system.

    Returns dict with 'items' (list of service orders, up to limit) and
    'total' (count of orders returned from API after filtering).
    """
    client = get_client()

    try:
        response = get_work_orders.sync_detailed(
            client=client,
            status=status,
            company_id=company_id,
            work_order_number=work_order_number,
            assigned_employees=assigned_employees,
        )

        if response.parsed is None:
            raise ValueError("Failed to parse service orders")

        # Convert list of SDK models to dicts
        items = [
            item.to_dict() for item in response.parsed
        ] if response.parsed else []

        # Apply limit (API does not support server-side pagination)
        total = len(items)
        return {"items": items[:limit], "total": total}

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
            id=asset_id,
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
        raise ValueError(f"Error fetching asset {asset_id}: {str(e)}") from e


@mcp.tool()
def search_assets(
    query: Optional[str] = Field(
        default=None,
        description="Search query (name, serial number, model, etc.)",
    ),
    limit: int = Field(
        default=25,
        ge=1,
        le=100,
        description="Maximum items to return (1-100)",
    ),
    server_side: bool = Field(
        default=True,
        description="Use server-side filtering (faster for large datasets)",
    ),
) -> dict:
    """
    Search/list assets with optional filtering.

    When server_side=True (default): Uses server-side search for efficiency.
    The API returns up to limit matching results. 'total' reflects the count
    of results returned from the server.

    When server_side=False: Fetches all assets and filters client-side.
    'total' reflects all matching records across the entire dataset.

    Returns dict with 'items' (asset list, truncated to limit) and 'total'
    (count of matching assets in the result set).

    Server-side filtering recommended for production systems with many assets.
    """
    client = get_client()

    try:
        # Use server-side filtering if query provided
        if query and server_side:
            server_response = get_asset_manager_list.sync_detailed(
                client=client,
                model_search_string=query,
                model_page_size=limit,
            )

            if server_response.parsed is None:
                raise ValueError("Failed to parse assets")

            # Convert SDK models to dicts
            assets = [asset.to_dict() for asset in server_response.parsed]
            total = len(assets)
            return {"items": assets[:limit], "total": total}

        # Fall back to client-side filtering for all assets
        all_response = get_all_assets.sync_detailed(client=client)

        if all_response.parsed is None:
            raise ValueError("Failed to parse assets")

        # Convert list of SDK models to list of dicts
        assets = [asset.to_dict() for asset in all_response.parsed]

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

        # Calculate total before limiting (represents all matching results)
        total = len(assets)

        # Apply limit and return
        return {"items": assets[:limit], "total": total}

    except ValueError:
        # Re-raise ValueError as-is
        raise
    except Exception as e:
        raise ValueError(f"Error searching assets: {str(e)}") from e


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
