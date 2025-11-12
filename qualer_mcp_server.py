"""
Qualer MCP Server

Production-ready MCP server wrapping the Qualer SDK for AI agent integration.
Exposes Qualer API operations as MCP tools and read-only data as resources.
"""

from __future__ import annotations

import base64
import os
from typing import Any, Optional

import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field


# ============================================================================
# Configuration & Client
# ============================================================================

# Global client initialized in main()
_client: Optional[httpx.AsyncClient] = None


def get_client() -> httpx.AsyncClient:
    """Get the initialized Qualer API client."""
    if _client is None:
        raise RuntimeError("Qualer client not initialized")
    return _client


async def init_client() -> httpx.AsyncClient:
    """Initialize Qualer API client with auth from environment."""
    base_url = os.environ.get(
        "QUALER_BASE_URL", "https://jgiquality.qualer.com"
    )
    token = os.environ.get("QUALER_TOKEN", "")

    if not token:
        raise RuntimeError(
            "QUALER_TOKEN environment variable is required. "
            "Set it in your shell or MCP client config."
        )

    # Create HTTP client with auth header
    return httpx.AsyncClient(
        base_url=base_url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        timeout=30.0,
    )


async def close_client(client: httpx.AsyncClient) -> None:
    """Clean up HTTP client on shutdown."""
    await client.aclose()


# ============================================================================
# MCP Server Setup
# ============================================================================


mcp = FastMCP(
    "Qualer SDK",
    dependencies=["httpx", "pydantic"],
)


# ============================================================================
# Pydantic Models (Structured Schemas for Agent Reasoning)
# ============================================================================


class ServiceOrder(BaseModel):
    """Service order entity from Qualer API."""

    id: int
    number: str = Field(
        description="Service order number (e.g., SO-12345)"
    )
    status: str = Field(
        description="Current status (e.g., Open, In Progress, Closed)"
    )
    client_company_id: Optional[int] = None
    client_company_name: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class Asset(BaseModel):
    """Asset/equipment entity from Qualer API."""

    id: int
    name: str = Field(description="Asset name or description")
    serial_number: Optional[str] = Field(
        None, description="Serial number or identifier"
    )
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    client_company_id: Optional[int] = None
    location: Optional[str] = None


class Document(BaseModel):
    """Document metadata from Qualer API."""

    id: int
    filename: str
    uploaded_at: Optional[str] = None
    uploaded_by: Optional[str] = None
    size_bytes: Optional[int] = None


class PaginatedResponse(BaseModel):
    """Generic paginated response wrapper."""

    items: list[Any] = Field(
        description="List of items in current page"
    )
    next_cursor: Optional[str] = Field(
        None, description="Cursor token for next page"
    )
    total_count: Optional[int] = Field(
        None, description="Total items (if available)"
    )


class UploadResult(BaseModel):
    """Result of document upload operation."""

    success: bool
    document_id: Optional[int] = None
    message: str


# ============================================================================
# MCP Tools (Side-Effect Operations)
# ============================================================================


@mcp.tool()
async def get_service_order(
    so_id: int = Field(description="Service order ID to retrieve"),
) -> ServiceOrder:
    """
    Fetch a single service order by its ID.

    Returns full details including status, client info, and timestamps.
    Use this when you need current information about a specific SO.
    """
    client = get_client()

    try:
        response = await client.get(f"/api/v1/service-orders/{so_id}")
        response.raise_for_status()
        data = response.json()
        return ServiceOrder(**data)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise ValueError(f"Service order {so_id} not found")
        raise RuntimeError(
            f"API error: {e.response.status_code} - {e.response.text}"
        )


@mcp.tool()
async def search_service_orders(
    status: Optional[str] = Field(
        None, description="Filter by status (e.g., Open, Closed)"
    ),
    client_company_id: Optional[int] = Field(
        None, description="Filter by client company ID"
    ),
    limit: int = Field(
        25, description="Maximum items to return (1-100)", ge=1, le=100
    ),
    cursor: Optional[str] = Field(
        None, description="Pagination cursor from previous response"
    ),
) -> PaginatedResponse:
    """
    Search service orders with optional filters and pagination.

    Supports filtering by status and client company. Returns paginated
    results with a cursor token for fetching additional pages.
    """
    client = get_client()

    params: dict[str, Any] = {"limit": limit}
    if status:
        params["status"] = status
    if client_company_id:
        params["client_company_id"] = client_company_id
    if cursor:
        params["cursor"] = cursor

    try:
        response = await client.get(
            "/api/v1/service-orders", params=params
        )
        response.raise_for_status()
        data = response.json()

        items = [ServiceOrder(**item) for item in data.get("items", [])]
        return PaginatedResponse(
            items=items,
            next_cursor=data.get("next_cursor"),
            total_count=data.get("total_count"),
        )
    except httpx.HTTPStatusError as e:
        raise RuntimeError(
            f"API error: {e.response.status_code} - {e.response.text}"
        )


@mcp.tool()
async def get_asset(
    asset_id: int = Field(description="Asset ID to retrieve"),
) -> Asset:
    """
    Fetch a single asset/equipment record by its ID.

    Returns full details including serial number, model, manufacturer,
    and location.
    """
    client = get_client()

    try:
        response = await client.get(f"/api/v1/assets/{asset_id}")
        response.raise_for_status()
        data = response.json()
        return Asset(**data)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise ValueError(f"Asset {asset_id} not found")
        raise RuntimeError(
            f"API error: {e.response.status_code} - {e.response.text}"
        )


@mcp.tool()
async def search_assets(
    query: str = Field(
        description="Search query (name, serial number, model, etc.)"
    ),
    client_company_id: Optional[int] = Field(
        None, description="Filter by client company ID"
    ),
    limit: int = Field(
        25, description="Maximum items to return (1-100)", ge=1, le=100
    ),
    cursor: Optional[str] = Field(
        None, description="Pagination cursor from previous response"
    ),
) -> PaginatedResponse:
    """
    Search assets with free-text query and optional filters.

    The query searches across asset name, serial number, model, and
    manufacturer. Returns paginated results with cursor token for
    additional pages.
    """
    client = get_client()

    params: dict[str, Any] = {"q": query, "limit": limit}
    if client_company_id:
        params["client_company_id"] = client_company_id
    if cursor:
        params["cursor"] = cursor

    try:
        response = await client.get(
            "/api/v1/assets/search", params=params
        )
        response.raise_for_status()
        data = response.json()

        items = [Asset(**item) for item in data.get("items", [])]
        return PaginatedResponse(
            items=items,
            next_cursor=data.get("next_cursor"),
            total_count=data.get("total_count"),
        )
    except httpx.HTTPStatusError as e:
        raise RuntimeError(
            f"API error: {e.response.status_code} - {e.response.text}"
        )


@mcp.tool()
async def upload_document_to_service_order(
    so_id: int = Field(
        description="Service order ID to attach document to"
    ),
    filename: str = Field(description="Document filename with extension"),
    content_base64: str = Field(
        description="Base64-encoded file content"
    ),
) -> UploadResult:
    """
    Upload and attach a document to a service order.

    The document content must be base64-encoded. Common use cases:
    - Certificates of calibration
    - Test reports
    - Photos of equipment
    - Customer correspondence

    Returns upload result with document ID on success.
    """
    client = get_client()

    # Validate base64
    try:
        content_bytes = base64.b64decode(content_base64)
    except Exception as e:
        return UploadResult(
            success=False, message=f"Invalid base64 encoding: {e}"
        )

    payload = {
        "filename": filename,
        "content": content_base64,
    }

    try:
        response = await client.post(
            f"/api/v1/service-orders/{so_id}/documents", json=payload
        )
        response.raise_for_status()
        data = response.json()

        return UploadResult(
            success=True,
            document_id=data.get("id"),
            message=f"Uploaded {filename} ({len(content_bytes)} bytes)",
        )
    except httpx.HTTPStatusError as e:
        return UploadResult(
            success=False,
            message=(
                f"Upload failed: {e.response.status_code} - "
                f"{e.response.text}"
            ),
        )


@mcp.tool()
async def list_service_order_documents(
    so_id: int = Field(
        description="Service order ID to list documents for"
    ),
) -> list[Document]:
    """
    List all documents attached to a service order.

    Returns metadata for each document (filename, upload time, size).
    Use get_service_order_document to retrieve actual file content.
    """
    client = get_client()

    try:
        response = await client.get(
            f"/api/v1/service-orders/{so_id}/documents"
        )
        response.raise_for_status()
        data = response.json()

        return [Document(**doc) for doc in data.get("documents", [])]
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise ValueError(f"Service order {so_id} not found")
        raise RuntimeError(
            f"API error: {e.response.status_code} - {e.response.text}"
        )


# ============================================================================
# MCP Resources (Read-Only Context for Agent)
# ============================================================================


@mcp.resource("qualer://service-order/{so_id}")
async def service_order_resource(so_id: int) -> str:
    """
    Read-only view of a service order as formatted JSON.

    Use this resource when you need to load service order context
    without making a direct API call. Ideal for agent reasoning tasks.
    """
    so = await get_service_order(so_id)
    return so.model_dump_json(indent=2)


@mcp.resource("qualer://asset/{asset_id}")
async def asset_resource(asset_id: int) -> str:
    """
    Read-only view of an asset as formatted JSON.

    Use this resource when you need to load asset/equipment context
    without making a direct API call. Ideal for agent reasoning tasks.
    """
    asset = await get_asset(asset_id)
    return asset.model_dump_json(indent=2)


# ============================================================================
# Server Entrypoint
# ============================================================================


async def main():
    """Launch MCP server over stdio transport."""
    global _client
    _client = await init_client()
    try:
        # Run the MCP server
        mcp.run()
    finally:
        await close_client(_client)


if __name__ == "__main__":
    import asyncio
    # CRITICAL: Never print to stdout on stdio transport
    asyncio.run(main())
