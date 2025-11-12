# Qualer MCP Server - Setup Checklist

Use this checklist to verify your setup is complete and working.

## Prerequisites

- [ ] Python 3.10 or higher installed
  ```powershell
  python --version
  # Should show: Python 3.10.x or higher
  ```

- [ ] Qualer API token available
  - Contact Johnson Gage Quality Inspection Inc. for API access
  - Token should have permissions for service orders, assets, documents

- [ ] Git installed (optional, for version control)
  ```powershell
  git --version
  ```

## Installation

- [ ] Clone or download this repository
  ```powershell
  git clone <repo-url>
  cd qualer_mcp
  ```

- [ ] Install Python dependencies
  ```powershell
  pip install -r requirements.txt
  ```

- [ ] Verify MCP CLI is installed
  ```powershell
  mcp --version
  # Should show mcp version info
  ```

## Configuration

- [ ] Set environment variables

  **Option A: PowerShell (current session)**
  ```powershell
  $env:QUALER_BASE_URL = "https://jgiquality.qualer.com"
  $env:QUALER_TOKEN = "your_actual_token_here"
  ```

  **Option B: Permanent (user-level)**
  ```powershell
  setx QUALER_BASE_URL "https://jgiquality.qualer.com"
  setx QUALER_TOKEN "your_actual_token_here"
  # Restart terminal after this
  ```

  **Option C: Use setup script**
  ```powershell
  .\setup.ps1
  # Follow interactive prompts
  ```

- [ ] Verify environment variables are set
  ```powershell
  echo $env:QUALER_BASE_URL
  echo $env:QUALER_TOKEN
  ```

## Testing

- [ ] Run MCP dev inspector
  ```powershell
  mcp dev qualer_mcp_server.py
  ```

- [ ] Verify dev inspector opens in browser
  - Should see list of 5 tools
  - Should see list of 2 resources

- [ ] Test a tool in dev inspector
  - Try: `get_service_order` with a known service order ID
  - Should return ServiceOrder JSON
  - Should not show authentication errors

- [ ] Test a resource in dev inspector
  - Try: `qualer://service-order/12345`
  - Should return formatted JSON

- [ ] Run unit tests (optional)
  ```powershell
  pytest test_qualer_mcp.py
  # Should show 5 passing tests
  ```

## Claude Desktop Integration

- [ ] Locate Claude Desktop config directory
  - Windows: `%APPDATA%\Claude\`
  - Navigate there: `cd $env:APPDATA\Claude`

- [ ] Backup existing config (if any)
  ```powershell
  Copy-Item claude_desktop_config.json claude_desktop_config.json.backup
  ```

- [ ] Copy example config
  ```powershell
  # From qualer_mcp repo directory
  Copy-Item claude_desktop_config.json $env:APPDATA\Claude\
  ```

- [ ] Edit config with your token
  - Open `%APPDATA%\Claude\claude_desktop_config.json`
  - Replace `"QUALER_TOKEN": ""` with your actual token
  - Save the file

- [ ] Restart Claude Desktop
  - Completely quit Claude Desktop
  - Launch Claude Desktop again

- [ ] Verify MCP connection in Claude
  - Look for 🔌 icon in Claude interface
  - Should show "Qualer SDK" as connected

- [ ] Test with a query
  - Ask Claude: "Show me service order 12345"
  - Claude should call the MCP tool
  - Should return actual data from Qualer API

## Continue.dev Integration (VS Code)

- [ ] Install Continue extension in VS Code
  - Open VS Code
  - Go to Extensions (Ctrl+Shift+X)
  - Search for "Continue"
  - Click Install

- [ ] Create Continue config directory
  ```powershell
  mkdir $HOME\.continue -ErrorAction SilentlyContinue
  ```

- [ ] Copy example config
  ```powershell
  Copy-Item continue_config.yaml $HOME\.continue\config.yaml
  ```

- [ ] Edit config if needed
  - Verify QUALER_TOKEN environment variable is set
  - Or hardcode token in config (less secure)

- [ ] Reload VS Code
  - Restart VS Code or reload window

- [ ] Test in Continue chat
  - Open Continue chat panel
  - Ask: "What service orders are open?"
  - Should call Qualer MCP tools

## Troubleshooting

### MCP dev inspector won't start

- [ ] Check Python version is 3.10+
- [ ] Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`
- [ ] Try running directly: `python -m mcp dev qualer_mcp_server`

### "QUALER_TOKEN missing" error

- [ ] Verify env var is set: `echo $env:QUALER_TOKEN`
- [ ] If using permanent setx, restart terminal
- [ ] Check config file has token (Claude/Continue)

### "Cannot import httpx" or similar

- [ ] Install missing dependency: `pip install httpx`
- [ ] Or reinstall all: `pip install -r requirements.txt`

### "Connection refused" or API errors

- [ ] Verify QUALER_BASE_URL is correct
- [ ] Test API directly with curl/Postman
- [ ] Check firewall/proxy settings
- [ ] Verify token has correct permissions

### Claude Desktop doesn't show MCP tools

- [ ] Check config file location is correct
- [ ] Verify JSON syntax in config file (use JSONLint)
- [ ] Check Claude Desktop logs (Help → View Logs)
- [ ] Try running server manually: `python -m qualer_mcp_server`

### Tools return errors in Claude

- [ ] Check QUALER_TOKEN is valid
- [ ] Verify API endpoints match your Qualer instance
- [ ] Test same API call with curl to isolate issue

## Customization

- [ ] Review Pydantic models in `qualer_mcp_server.py`
  - Match field names to your Qualer API schema
  - Add missing fields

- [ ] Update API endpoints if needed
  - Search for `/api/v1/` in code
  - Replace with your actual endpoints

- [ ] Add new tools for additional Qualer endpoints
  - Copy existing tool pattern
  - Update schemas

- [ ] Test changes with `mcp dev`

## Production Readiness

- [ ] Use secret management instead of env vars
  - Azure Key Vault
  - AWS Secrets Manager
  - HashiCorp Vault

- [ ] Add rate limiting logic
  - Detect 429 responses
  - Implement exponential backoff

- [ ] Add structured logging
  - Log to stderr (not stdout)
  - Include request IDs
  - Structured JSON logs

- [ ] Implement monitoring
  - Track tool usage
  - Monitor error rates
  - Alert on failures

- [ ] Set up CI/CD
  - Run tests on commit
  - Auto-deploy to production

## Next Steps

- [ ] Read `README.md` for detailed documentation
- [ ] Review `ARCHITECTURE.md` to understand system design
- [ ] Follow `QUICKSTART.md` for rapid testing
- [ ] Read `PROJECT_SUMMARY.md` for overview

## Support Resources

- [ ] Bookmark MCP documentation: https://modelcontextprotocol.io/
- [ ] Join MCP community discussions
- [ ] Contact Qualer support for API questions
- [ ] File issues in this repo for MCP integration bugs

---

**Completion Status**: ____ / ____ items checked

**Last Updated**: _______________

**Notes**:
```

```
