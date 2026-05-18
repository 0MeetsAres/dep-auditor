# dep-auditor MCP Server

Package Security & License Auditor — an MCP server that checks package licenses, known vulnerabilities, and metadata across **npm**, **PyPI**, and **Cargo**.

Built for AI agents (Claude, Cursor, Windsurf, etc.) to autonomously audit dependencies.

## Tools

| Tool | Description |
|------|-------------|
| `check_package` | Get package license, version, description, maintainers |
| `audit_vulns` | Check for known CVEs via OSV.dev database |

## Usage with Claude Desktop

```json
{
  "mcpServers": {
    "dep-auditor": {
      "command": "python",
      "args": ["path/to/main.py"]
    }
  }
}
```

## Deployment

### Manual

```bash
pip install -r requirements.txt
python main.py
```


