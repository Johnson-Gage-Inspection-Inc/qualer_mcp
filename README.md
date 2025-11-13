# Qualer MCP Server

Production-ready MCP server wrapping the Qualer SDK for AI agent integration. Exposes Qualer API operations as MCP tools and read-only data as MCP resources, enabling AI assistants in Claude Desktop, Continue, Cursor, and VS Code Copilot to interact with your Qualer quality management system.

## Features

- **MCP Tools** for side-effect operations:
  - `get_service_order` - Fetch service order by ID
  - `search_service_orders` - Search with filters and pagination
  - `get_asset` - Fetch asset/equipment by ID
  - `search_assets` - Free-text asset search
  - `list_service_order_documents` - List service order document metadata
  - `list_work_item_documents` - List work item document metadata

- **MCP Resources** for read-only context:
  - `qualer://service-order/{id}` - Service order as JSON
  - `qualer://asset/{id}` - Asset as JSON

- **Production-ready features**:
  - Structured Pydantic schemas for agent reasoning
  - Pagination with cursor tokens
  - Proper error handling and HTTP status codes
  - Bearer token authentication
  - stdio transport (no stdout pollution)

## Quick Start

### 1. Install Dependencies

```powershell
# Using pip
pip install -r requirements.txt

# Or with the MCP CLI
pip install "mcp[cli]"
```

### 2. Set Environment Variables

```powershell
# Windows PowerShell
$env:QUALER_BASE_URL = "https://jgiquality.qualer.com"
$env:QUALER_TOKEN = "your_api_token_here"

# Or permanently
setx QUALER_BASE_URL "https://jgiquality.qualer.com"
setx QUALER_TOKEN "your_api_token_here"
```

Alternatively, copy `.env.example` to `.env` and fill in your values.

### 3. Run Tests

**Using pytest (recommended):**

```powershell
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_server.py -v

# Run with coverage
python -m pytest tests/ --cov=qualer_mcp_server
```

Test files include:
- `tests/test_server.py` - Server initialization and structure
- `tests/test_api_call.py` - Integration tests with real API calls  
- `tests/test_qualer_mcp.py` - Tool availability tests

**Optional: Using MCP dev inspector (requires uv)**

```powershell
# Install uv if not already installed
pip install uv

# Then run the dev inspector
mcp dev qualer_mcp_server.py
```

The MCP dev inspector provides an interactive UI to test tools, inspect schemas, and try resources.

## Editor Integration

### Claude Desktop

1. Locate your Claude Desktop config:
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. Add the Qualer MCP server configuration:

```json
{
  "mcpServers": {
    "qualer": {
      "command": "python",
      "args": ["-m", "qualer_mcp_server"],
      "env": {
        "QUALER_BASE_URL": "https://jgiquality.qualer.com",
        "QUALER_TOKEN": "your_api_token_here"
      }
    }
  }
}
```

3. Restart Claude Desktop

You can also copy `claude_desktop_config.json` from this repo as a template.

### Continue.dev (VS Code)

1. Create or edit `.continue/config.yaml` in your workspace:

```yaml
mcpServers:
  - name: Qualer
    command: python
    args:
      - "-m"
      - "qualer_mcp_server"
    env:
      QUALER_BASE_URL: https://jgiquality.qualer.com
      QUALER_TOKEN: ${env:QUALER_TOKEN}
```

2. Reload VS Code

You can also copy `continue_config.yaml` from this repo as a template.

### Cursor / VS Code Copilot

Similar to Continue, add the server to your workspace MCP configuration. Refer to your editor's MCP documentation for specific config file locations.

## Usage Examples

Once integrated, you can ask your AI assistant:

- "Show me service order 12345"
- "Search for assets with serial number X123"
- "List all open service orders for client company 42"
- "What documents are attached to service order 456?"

The AI will automatically call the appropriate MCP tools and present results in a conversational format.

## API Endpoints

The server expects the following Qualer API endpoints (adjust in code if needed):

- `GET /api/v1/service-orders/{id}` - Get service order
- `GET /api/v1/service-orders?status=...&limit=...&cursor=...` - Search service orders
- `GET /api/v1/assets/{id}` - Get asset
- `GET /api/v1/assets` - List/search assets (server-side filtering)
- `GET /api/v1/service-orders/{id}/documents` - List service order documents
- `GET /api/v1/service-order-items/{id}/documents` - List work item documents

## Customization

### Adding New Tools

```python
@mcp.tool()
def your_new_tool(
    param: str = Field(description="Your parameter"),
) -> YourModel:
    """
    Tool description for the AI agent.
    """
    client = get_client()
    response = client.get(f"/api/v1/your-endpoint/{param}")
    response.raise_for_status()
    return YourModel(**response.json())
```

### Adding New Resources

```python
@mcp.resource("qualer://your-resource/{id}")
def your_resource(id: int) -> str:
    """Read-only resource description."""
    data = your_tool(id)
    return data.model_dump_json(indent=2)
```

### Pydantic Models

Use strict Pydantic models with field descriptions for better agent reasoning:

```python
class YourModel(BaseModel):
    id: int
    name: str = Field(description="Clear description for AI")
    status: str = Field(description="Enum-like description")
```

## Development

### Run Tests

```powershell
pytest
```

### Format Code

```powershell
black qualer_mcp_server.py
ruff check qualer_mcp_server.py
```

### Type Checking

The code uses Python 3.10+ type hints. Use a type checker like Pylance or mypy:

```powershell
pip install mypy
mypy qualer_mcp_server.py
```

## Troubleshooting

### "QUALER_TOKEN missing" error

Set the `QUALER_TOKEN` environment variable in your shell or MCP client config.

### "Qualer client not initialized" error

The global client failed to initialize. Check that `QUALER_TOKEN` is set and the server can reach `QUALER_BASE_URL`.

### stdio transport issues

Never use `print()` in MCP tools/resources when running over stdio. Use logging to stderr if needed:

```python
import sys
print("Debug info", file=sys.stderr)
```

### API endpoint mismatches

If your Qualer instance uses different endpoints, update the URLs in the tool functions (e.g., `/api/v1/service-orders` → `/api/v2/orders`).

## Production Hardening

- **Rate limiting**: Add exponential backoff for 429 responses
- **Auth refresh**: Implement token refresh if Qualer supports it
- **Secrets management**: Use a secret store instead of env vars
- **Monitoring**: Log errors to stderr with structured logging
- **Schema validation**: Tighten Field constraints (enums, ranges)

## Resources

- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [FastMCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Claude Desktop MCP Guide](https://docs.anthropic.com/claude/docs/model-context-protocol)
- [Continue.dev MCP Documentation](https://docs.continue.dev/customize/deep-dives/mcp)

## License

MIT (adjust as needed for your organization)

## Support

For Qualer API questions, contact Johnson Gage Quality Inspection Inc.

For MCP integration issues, see the [MCP community](https://github.com/modelcontextprotocol/python-sdk/issues).
