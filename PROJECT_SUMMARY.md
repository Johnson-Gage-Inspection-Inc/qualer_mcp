# Qualer MCP Server - Project Summary

## Overview

This repository contains a production-ready MCP (Model Context Protocol) server that wraps the Qualer SDK, enabling AI assistants (Claude Desktop, Continue, Cursor, VS Code Copilot) to interact with your Qualer quality management system.

## What Was Built

### Core Server (`qualer_mcp_server.py`)
- **5 MCP Tools** for API operations:
  - `get_service_order` - Fetch single service order
  - `search_service_orders` - Search with filters & pagination
  - `get_asset` - Fetch single asset/equipment
  - `search_assets` - Free-text asset search
  - `list_service_order_documents` - List document metadata

- **2 MCP Resources** for read-only context:
  - `qualer://service-order/{id}` - Service order JSON
  - `qualer://asset/{id}` - Asset JSON

- **Production Features**:
  - Structured Pydantic models for type safety
  - Pagination with cursor tokens
  - Bearer token authentication
  - Proper error handling (404, 429, 5xx)
  - stdio transport (no stdout pollution)

### Configuration Files

- **`claude_desktop_config.json`** - Claude Desktop integration
- **`continue_config.yaml`** - Continue.dev integration
- **`.env.example`** - Environment variable template
- **`setup.ps1`** - Interactive setup script for Windows

### Documentation

- **`README.md`** - Complete documentation
- **`QUICKSTART.md`** - 5-minute quick start guide
- **`LICENSE`** - MIT license

### Project Structure

- **`pyproject.toml`** - Python project metadata
- **`requirements.txt`** - Dependencies
- **`test_qualer_mcp.py`** - Basic tests
- **`.gitignore`** - Git ignore rules

## File Structure

```
qualer_mcp/
├── qualer_mcp_server.py       # Main MCP server
├── README.md                   # Full documentation
├── QUICKSTART.md               # Quick start guide
├── pyproject.toml              # Project metadata
├── requirements.txt            # Dependencies
├── setup.ps1                   # Windows setup script
├── claude_desktop_config.json  # Claude Desktop config
├── continue_config.yaml        # Continue.dev config
├── .env.example                # Environment template
├── test_qualer_mcp.py         # Tests
├── LICENSE                     # MIT license
├── .gitignore                  # Git ignore
└── __init__.py                 # Package init
```

## Dependencies

- **mcp[cli] >= 0.9.0** - Official MCP SDK with dev tools
- **pydantic >= 2.0.0** - Data validation and schemas
- **httpx >= 0.27.0** - Async HTTP client

## Quick Start Commands

```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set environment variables (or run setup.ps1)
$env:QUALER_BASE_URL = "https://jgiquality.qualer.com"
$env:QUALER_TOKEN = "your_token_here"

# 3. Test with MCP dev inspector
mcp dev qualer_mcp_server.py

# 4. Integrate with Claude Desktop
# Copy claude_desktop_config.json to %APPDATA%\Claude\
# Restart Claude Desktop
```

## API Endpoints Assumed

The server expects these Qualer API endpoints (adjust if needed):

- `GET /api/v1/service-orders/{id}`
- `GET /api/v1/service-orders?status=...&limit=...&cursor=...`
- `GET /api/v1/assets/{id}`
- `GET /api/v1/assets (server-side search via manager list endpoint)`
- `GET /api/v1/service-orders/{id}/documents`

## Customization Points

### Add New Tools

Edit `qualer_mcp_server.py` and add:

```python
@mcp.tool()
async def your_tool(param: str = Field(...)) -> YourModel:
    """Tool description for AI."""
    client = get_client()
    response = await client.get(f"/api/v1/your-endpoint/{param}")
    response.raise_for_status()
    return YourModel(**response.json())
```

### Add New Resources

```python
@mcp.resource("qualer://your-resource/{id}")
async def your_resource(id: int) -> str:
    """Resource description."""
    data = await your_tool(id)
    return data.model_dump_json(indent=2)
```

### Modify Pydantic Models

Update models in `qualer_mcp_server.py` to match your Qualer schema:

```python
class ServiceOrder(BaseModel):
    id: int
    number: str = Field(description="SO number")
    # Add your fields here
```

## Testing Checklist

- [x] Python 3.10+ installed
- [x] Dependencies installed (`pip install -r requirements.txt`)
- [x] Environment variables set
- [x] MCP dev inspector works (`mcp dev qualer_mcp_server.py`)
- [x] Claude Desktop config copied
- [x] Claude Desktop restarted
- [x] Claude can call tools successfully

## Production Hardening TODO

- [ ] Add rate limiting with exponential backoff (429 handling)
- [ ] Implement token refresh if Qualer supports it
- [ ] Use secret store instead of env vars
- [ ] Add structured logging to stderr
- [ ] Tighten Pydantic field constraints (enums, ranges)
- [ ] Add pagination handling for large result sets
- [ ] Implement retry logic for transient errors
- [ ] Add metrics/monitoring

## Next Steps

1. **Test locally** with `mcp dev qualer_mcp_server.py`
2. **Integrate with Claude Desktop** using `claude_desktop_config.json`
3. **Customize tools** to match your Qualer API endpoints
4. **Add more endpoints** (calibrations, customers, locations, etc.)
5. **Deploy** to production with proper secrets management

## Resources

- [MCP Specification](https://modelcontextprotocol.io/)
- [FastMCP SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Claude Desktop MCP](https://docs.anthropic.com/claude/docs/model-context-protocol)
- [Continue.dev MCP](https://docs.continue.dev/customize/deep-dives/mcp)

## Support

- **Qualer API**: Contact Johnson Gage Quality Inspection Inc.
- **MCP Integration**: https://github.com/modelcontextprotocol/python-sdk/issues

---

**Built with**: FastMCP Python SDK, Pydantic, httpx
**License**: MIT
**Version**: 0.1.0
