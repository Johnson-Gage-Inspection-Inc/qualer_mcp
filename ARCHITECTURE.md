# Qualer MCP Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      AI Assistant Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │    Claude    │  │  Continue.dev│  │    Cursor    │          │
│  │   Desktop    │  │   (VS Code)  │  │  VS Code CP  │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                   │
│         └─────────────────┼─────────────────┘                   │
│                           │                                     │
│                    MCP Protocol (stdio)                         │
│                           │                                     │
└───────────────────────────┼─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Qualer MCP Server                              │
│                (qualer_mcp_server.py)                           │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    MCP Tools (5)                         │  │
│  │  • get_service_order                                     │  │
│  │  • search_service_orders                                 │  │
│  │  • get_asset                                             │  │
│  │  • search_assets                                         │  │
│  │  • list_service_order_documents                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  MCP Resources (2)                       │  │
│  │  • qualer://service-order/{id}                           │  │
│  │  • qualer://asset/{id}                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Pydantic Models (Schemas)                   │  │
│  │  • ServiceOrder                                          │  │
│  │  • Asset                                                 │  │
│  │  • Document                                              │  │
│  │  • PaginatedResponse                                     │  │
│  │  • UploadResult                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              HTTP Client (httpx)                         │  │
│  │  • Bearer Token Authentication                           │  │
│  │  • Async Request Handling                                │  │
│  │  • Error Handling (404, 429, 5xx)                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                    HTTPS REST API
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Qualer API                                 │
│               (jgiquality.qualer.com)                           │
│                                                                 │
│  Endpoints:                                                     │
│  • GET  /api/v1/service-orders/{id}                             │
│  • GET  /api/v1/service-orders?status=...&limit=...&cursor=...  │
│  • GET  /api/v1/assets/{id}                                     │
│  • GET  /api/v1/assets (client-side filtering applied)          │
│  • GET  /api/v1/service-orders/{id}/documents                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Example

**User asks Claude**: "Show me service order 12345"

```
1. Claude Desktop
   └─> Calls MCP tool: get_service_order(so_id=12345)
       
2. Qualer MCP Server
   └─> HTTP GET /api/v1/service-orders/12345
       Headers: Authorization: Bearer {QUALER_TOKEN}
       
3. Qualer API
   └─> Returns JSON: {id: 12345, number: "SO-12345", status: "Open", ...}
       
4. Qualer MCP Server
   └─> Validates response with ServiceOrder Pydantic model
   └─> Returns structured data to Claude
       
5. Claude Desktop
   └─> Presents result: "Service Order SO-12345 is currently Open..."
```

## Configuration Flow

```
Environment Variables          MCP Client Config
┌─────────────────┐           ┌──────────────────────┐
│ QUALER_BASE_URL │ ────────> │ claude_desktop_      │
│ QUALER_TOKEN    │           │   config.json        │
└─────────────────┘           │                      │
                              │ or                   │
                              │                      │
                              │ continue_config.yaml │
                              └──────────┬───────────┘
                                         │
                                         ▼
                              ┌──────────────────────┐
                              │  MCP Server Launch   │
                              │  python -m           │
                              │  qualer_mcp_server   │
                              └──────────┬───────────┘
                                         │
                                         ▼
                              ┌──────────────────────┐
                              │   HTTP Client Init   │
                              │   with Bearer Token  │
                              └──────────────────────┘
```

## Security Model

```
┌─────────────────────────────────────────────────────────────────┐
│  User sets QUALER_TOKEN in:                                     │
│  • Environment variables (shell)                                │
│  • MCP client config (Claude/Continue)                          │
│  • .env file (development only)                                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  MCP Server reads token at startup                              │
│  • Validates token exists                                       │
│  • Creates HTTP client with Authorization header                │
│  • Token never logged or printed                                │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  All API requests include:                                      │
│  Authorization: Bearer {QUALER_TOKEN}                           │
│  Content-Type: application/json                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Development Workflow

```
1. Code Change
   └─> Edit qualer_mcp_server.py
   
2. Test Locally
   └─> mcp dev qualer_mcp_server.py
   └─> Interactive browser UI opens
   └─> Test tools with sample inputs
   
3. Check Errors
   └─> View error messages in terminal
   └─> Fix issues, repeat step 2
   
4. Test in Editor
   └─> Restart Claude Desktop / Continue
   └─> Ask AI assistant to use new tools
   └─> Verify results
   
5. Commit
   └─> git add .
   └─> git commit -m "Add new tool"
   └─> git push
```

## Deployment Options

### Local (Current Setup)
```
AI Assistant → stdio → MCP Server → HTTPS → Qualer API
```

### HTTP/SSE (Alternative)
```
AI Assistant → HTTP → MCP Server (ASGI) → HTTPS → Qualer API
              └─> Expose /.well-known/mcp/manifest.json
```

### Containerized
```
Docker Container:
  ├─ Python 3.10+
  ├─ qualer_mcp_server.py
  ├─ requirements.txt
  └─ Environment variables
  
AI Assistant → stdio/HTTP → Container → Qualer API
```
