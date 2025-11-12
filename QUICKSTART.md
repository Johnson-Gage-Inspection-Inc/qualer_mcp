# Qualer MCP Server - Quick Start Guide

This guide walks you through testing the MCP server in under 5 minutes.

## Prerequisites

- Python 3.10 or higher
- Qualer API token

## Step 1: Install Dependencies (30 seconds)

```powershell
pip install -r requirements.txt
```

## Step 2: Set Environment Variables (30 seconds)

```powershell
# PowerShell
$env:QUALER_BASE_URL = "https://jgiquality.qualer.com"
$env:QUALER_TOKEN = "your_actual_api_token_here"
```

Or copy `.env.example` to `.env` and fill in your token.

## Step 3: Test the Server (2 minutes)

**Option A: Quick validation (recommended)**

```powershell
python test_server.py
```

This will validate that:
- The module imports correctly
- Pydantic models work
- MCP server initializes

**Option B: Test with actual API call**

```powershell
python test_api_call.py
```

This will attempt to fetch a real service order from the API.

**Option C: Using MCP dev inspector (requires uv)**

```powershell
# Install uv first (one-time)
pip install uv

# Then launch the MCP dev inspector
mcp dev qualer_mcp_server.py
```

This opens an interactive UI in your browser where you can:
1. **View Tools** - See all available MCP tools
2. **Test Tools** - Call tools with test parameters and see results
3. **Inspect Schemas** - View Pydantic model schemas

## Step 4: Integrate with Claude Desktop (2 minutes)

1. Open Claude Desktop config:
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. Copy the contents of `claude_desktop_config.json` from this repo

3. Replace `your_api_token_here` with your actual Qualer token

4. Restart Claude Desktop

5. Ask Claude: "Show me service order 12345"

## Step 5: Verify It's Working

In Claude Desktop, you should see:
- A 🔌 icon indicating MCP tools are connected
- Claude can call Qualer tools when you ask questions
- Results formatted as conversational responses

## Common Issues

### "Cannot find module 'mcp'"
```powershell
pip install "mcp[cli]"
```

### "QUALER_TOKEN missing"
Set the environment variable in PowerShell or your MCP client config.

### "Connection refused"
Check that `QUALER_BASE_URL` is correct and accessible from your machine.

## Next Steps

- Read `README.md` for full documentation
- Customize tools in `qualer_mcp_server.py`
- Add more Qualer API endpoints
- Integrate with Continue.dev or Cursor

## Testing Without a Real Qualer Token

If you don't have a token yet, you can still test the server structure:

1. Comment out the token check in `init_client()`:
   ```python
   # if not token:
   #     raise RuntimeError("QUALER_TOKEN environment variable is required.")
   ```

2. Run `mcp dev qualer_mcp_server.py` to inspect schemas

3. Tools will fail at runtime, but you can verify the MCP setup works

## Support

- MCP issues: https://github.com/modelcontextprotocol/python-sdk
- Qualer API: Contact Johnson Gage Quality Inspection Inc.
